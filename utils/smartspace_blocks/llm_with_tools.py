import json
from typing import Annotated, Any, Generic, TypeVar, cast

import pydantic_core
from injector import inject
from litellm import Choices
from smartspace.core import (
    Config,
    GenericSchema,
    Output,
    State,
    WorkSpaceBlock,
    callback,
    metadata,
    step,
)
from smartspace.enums import BlockCategory
from smartspace.models import ContentItem

from app.blocks.native.llm.llm_tool import LLMTool
from app.blocks.native.llm.utils import (
    get_message_from_content_list,
    prepare_chat_history,
)
from app.integrations.blob_storage.core import BlobService
from app.integrations.llms.core import LLMFactory
from app.integrations.llms.models import (
    AssistantMessage,
    BaseChatFunction,
    BaseChatTool,
    ChatCompletionRequest,
    ModelConfig,
    ToolMessage,
    UserMessageContentList,
)
from app.utils.litellm import FinishReason, get_llm_response_type, get_llm_tool_calls

ResponseSchemaT = TypeVar("ResponseSchemaT", bound=dict[str, Any] | None)


@metadata(category=BlockCategory.AGENT)
class LLMWithTools(WorkSpaceBlock, Generic[ResponseSchemaT]):
    response: Output[ResponseSchemaT]

    llm_config: ModelConfig
    use_thread_history: Annotated[bool, Config()]
    response_schema: GenericSchema[ResponseSchemaT] = GenericSchema({"type": "string"})

    tools: dict[str, LLMTool]

    message: Annotated[
        list[ContentItem] | str,
        State(
            step_id="chat",
            input_ids=["message"],
        ),
    ] = []

    tool_calls: Annotated[
        dict[str, dict[str, Any]],
        State(
            step_id="chat",
            input_ids=["message"],
        ),
    ] = {}

    tool_messages: Annotated[
        list[AssistantMessage | ToolMessage],
        State(
            step_id="chat",
            input_ids=["message"],
        ),
    ] = []

    @inject
    def __init__(
        self,
        llm_factory: LLMFactory,
        blob_service: BlobService,
    ):
        super().__init__()

        self.llm_factory = llm_factory
        self.blob_service = blob_service

    def _schema_is_string(self):
        return (
            "type" not in self.response_schema
            or self.response_schema["type"] == "string"
        )

    @step()
    async def chat(self, message: list[ContentItem] | str):
        self.message = message
        await self._chat_inner()

    @callback()
    async def handle_tool_result(self, tool_call_id: str, tool_result: Any):
        self.tool_calls[tool_call_id] = {"result": tool_result}

        if all(["result" in tool_data for tool_data in self.tool_calls.values()]):
            tool_response_messages: list[ToolMessage] = []
            for tool_call_id, tool_data in self.tool_calls.items():
                content_str = pydantic_core.to_json(tool_data["result"]).decode()
                tool_response_messages.append(
                    ToolMessage(
                        content=content_str,
                        tool_call_id=tool_call_id,
                    )
                )

            self.tool_calls = {}

            self.tool_messages.extend(tool_response_messages)
            await self._chat_inner()

    async def _chat_inner(self):
        llm = await self.llm_factory.create_llm_from_model(self.llm_config)

        history = await prepare_chat_history(
            pre_prompt=self.llm_config.pre_prompt,
            thread_history=self.message_history if self.use_thread_history else [],
            blob_service=self.blob_service,
        )

        history.append(
            UserMessageContentList(
                content=await get_message_from_content_list(
                    content=self.message, blob_service=self.blob_service
                )
            )
        )

        history.extend(self.tool_messages)

        tools = [t.create_tool(name) for name, t in self.tools.items()]

        if self._schema_is_string():
            if (
                "type" in self.response_schema
                and self.response_schema["type"] == "object"
            ):
                parameters = self.response_schema
            else:
                parameters = {
                    "type": "object",
                    "properties": {"response": self.response_schema},
                }

            tools.append(
                BaseChatTool(
                    type="function",
                    function=BaseChatFunction(
                        name="_output_response",
                        description="This is your default tool. Use it to send your response to the user when there isn't another tool that should be called",
                        parameters=parameters,
                    ),
                )
            )

        if len(tools) == 0:
            request = ChatCompletionRequest(
                messages=history,
            )
        elif self._schema_is_string():
            request = ChatCompletionRequest(
                messages=history,
                tools=tools,
                tool_choice="required",
            )
        else:
            request = ChatCompletionRequest(
                messages=history,
                tools=tools,
                tool_choice="auto",
            )

        request = llm.remove_excess_tokens_chat_request(chat_request=request)

        llm_response = await llm.create_chat_completion(
            request=request,
            step_name=self.__class__.__name__,
        )

        if get_llm_response_type(llm_response=llm_response) == FinishReason.TOOL_CALLS:
            llm_tool_calls = get_llm_tool_calls(llm_response=llm_response)
            self.tool_messages.append(
                AssistantMessage(
                    content=llm_response.choices[0].message.content,  # type: ignore
                    tool_calls=llm_tool_calls,
                )
            )
            for tool_call in llm_tool_calls:
                args = json.loads(tool_call.function.arguments)
                if tool_call.function.name == "_output_response":
                    if self.response_schema and (
                        "type" not in self.response_schema
                        or self.response_schema["type"] != "object"
                    ):
                        args = args["response"] if "response" in args else args

                    self.response.send(args)
                else:
                    for name, tool in self.tools.items():
                        if name != tool_call.function.name:
                            continue

                        await tool.call(
                            (args["response"] if "response" in args else args)
                        ).then(
                            lambda result: self.handle_tool_result(
                                tool_call_id=tool_call.id,
                                tool_result=result,
                            )
                        )
                        self.tool_calls[tool_call.id] = {}
        else:
            choice = cast(Choices, llm_response.choices[0])

            self.response.send(choice.message.content)
