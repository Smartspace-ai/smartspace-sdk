import json
from typing import Annotated, Generic, TypeVar, cast

from injector import inject
from litellm import Choices  # type: ignore
from smartspace.core import (
    Config,
    GenericSchema,
    Output,
    WorkSpaceBlock,
    metadata,
    step,
)
from smartspace.enums import BlockCategory
from smartspace.models import ContentItem

from app.blocks.native.llm.utils import (
    get_message_from_content_list,
    prepare_chat_history,
)
from app.integrations.blob_storage.core import BlobService
from app.integrations.llms.core import LLMFactory
from app.integrations.llms.models import (
    BaseChatFunction,
    BaseChatTool,
    ChatCompletionRequest,
    FunctionCall,
    ModelConfig,
    ToolChoice,
    UserMessageContentList,
)
from app.utils.litellm import FinishReason, get_llm_response_type, get_llm_tool_calls

ResponseSchemaT = TypeVar("ResponseSchemaT")


@metadata(category=BlockCategory.AGENT)
class LLM(WorkSpaceBlock, Generic[ResponseSchemaT]):
    response: Output[ResponseSchemaT]

    llm_config: ModelConfig
    use_thread_history: Annotated[bool, Config()]
    response_schema: GenericSchema[ResponseSchemaT] = GenericSchema({"type": "string"})

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
        llm = await self.llm_factory.create_llm_from_model(self.llm_config)

        history = await prepare_chat_history(
            pre_prompt=self.llm_config.pre_prompt,
            thread_history=self.message_history if self.use_thread_history else [],
            blob_service=self.blob_service,
        )

        history.append(
            UserMessageContentList(
                content=await get_message_from_content_list(
                    content=message, blob_service=self.blob_service
                )
            )
        )

        if (
            "type" not in self.response_schema
            or self.response_schema["type"] == "string"
        ):
            request = ChatCompletionRequest(
                messages=history,
            )
        else:
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

            request = ChatCompletionRequest(
                messages=history,
                tools=[
                    BaseChatTool(
                        type="function",
                        function=BaseChatFunction(
                            name="output",
                            description="",
                            parameters=parameters,
                        ),
                    )
                ],
                tool_choice=ToolChoice(function=FunctionCall(name="output")),
            )

        request = llm.remove_excess_tokens_chat_request(chat_request=request)

        llm_response = await llm.create_chat_completion(
            request=request,
            step_name="LLM",
        )

        if get_llm_response_type(llm_response=llm_response) == FinishReason.TOOL_CALLS:
            llm_tool_calls = get_llm_tool_calls(llm_response=llm_response)
            args = json.loads(llm_tool_calls[0].function.arguments)

            if self.response_schema and (
                "type" not in self.response_schema
                or self.response_schema["type"] != "object"
            ):
                args = args["response"] if "response" in args else args

            self.response.send(args)
        else:
            choice = cast(Choices, llm_response.choices[0])

            self.response.send(choice.message.content)
