import json
import re
from functools import reduce
from typing import Annotated, Any, Generic, TypeVar

import pydantic_core
from injector import inject
from pydantic import BaseModel, Field
from smartspace.core import (
    GenericSchema,
    Output,
    WorkSpaceBlock,
    metadata,
    step,
)
from smartspace.enums import BlockCategory
from smartspace.models import ContentItem

from app.api.models import Source
from app.blocks.native.llm.utils import (
    get_message_from_content_list,
    prepare_chat_history,
)
from app.integrations.blob_storage.core import BlobService
from app.integrations.llms.core import LLM, LLMFactory
from app.integrations.llms.models import (
    BaseChatFunction,
    BaseChatTool,
    ChatCompletionRequest,
    FunctionCall,
    LLMError,
    MessageTypes,
    ModelConfig,
    ToolChoice,
    UserMessageContentList,
)
from app.integrations.search.models import SearchResult
from app.utils.litellm import FinishReason, get_llm_response_type, get_llm_tool_call


class FinalResultSource(BaseModel):
    name: str


ResponseSchemaT = TypeVar("ResponseSchemaT", bound=dict[str, Any] | None)


@metadata(category=BlockCategory.AGENT)
class Analyzer(WorkSpaceBlock, Generic[ResponseSchemaT]):
    class OutputFinalResultOutputBase(BaseModel):
        content: Any
        sources: list[FinalResultSource] | None = None

    class OutputFinalResultOutputString(BaseModel):
        content: str
        sources: list[FinalResultSource] | None = None

    response_schema: GenericSchema[ResponseSchemaT] = GenericSchema({"type": "string"})
    llm_config: ModelConfig

    sources: Output[list[Source]]
    content: Output[ResponseSchemaT]

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
    async def run(
        self,
        documents: list[SearchResult],
        message: list[ContentItem] | str,
    ):
        document_list = [
            f'{{"content": "{doc.content}", "name": "source_{i + 1}"}}'
            for i, doc in enumerate(documents)
        ]
        document_results = "[ " + ", ".join(document_list) + " ]"

        text = f"Here are the most relevant sources that were found in the knowledgebase. They might not have the information you need, but they're the closest sources that were found.\n{document_results}"

        if isinstance(message, list):
            message.append(ContentItem(text=text))
        else:
            message += "\n" + text

        if self._schema_is_string():
            pre_prompt = f"""Make sure to list the sources you used in the sources array like [{{"name": "source_1"}}].\nAny source from the knowledge base that you use in your response MUST be included in the sources array.\n{self.llm_config.pre_prompt}""".strip()
        else:
            pre_prompt = f"""Always cite the source of your information by inserting a citation in parentheses with a leading space, for example ' (source_1)', wherever the citation is relevant in the content field. Make sure to list corresponding citation indexes in the sources array like [{{"name": "source_1"}}].\nAny source from the knowledge base that you use in your response MUST be included in the sources array.\n{self.llm_config.pre_prompt}""".strip()

        chat_history = await prepare_chat_history(
            pre_prompt=pre_prompt,
            thread_history=self.message_history,
            blob_service=self.blob_service,
        )

        chat_history.append(
            UserMessageContentList(
                content=await get_message_from_content_list(
                    content=message, blob_service=self.blob_service
                )
            )
        )

        llm = await self.llm_factory.create_llm_from_model(self.llm_config)

        output_final_result_request = self._get_output_final_result_request(
            chat_history=chat_history,
            llm=llm,
        )

        output_final_result_response = await llm.create_chat_completion(
            request=output_final_result_request,
            step_name=self.__class__.__name__,
        )

        llm_response_type = get_llm_response_type(
            llm_response=output_final_result_response
        )

        if llm_response_type == FinishReason.STOP:
            if output_final_result_response.choices[0].message.content is None:  # type: ignore
                raise LLMError(message="Agent response is null")

            self.content.send(output_final_result_response.choices[0].message.content)  # type: ignore
            self.sources.send([])
            return

        elif llm_response_type == FinishReason.TOOL_CALLS:
            output_final_result_tool_call = get_llm_tool_call(
                llm_response=output_final_result_response
            )

            # if there is a json schema, the argumennts['content'] won't be a string so we don't want to run the fix_json_escaping method
            if self._schema_is_string():
                args = output_final_result_tool_call.arguments
            else:
                args = self._fix_json_escaping(output_final_result_tool_call.arguments)

            result = Analyzer.OutputFinalResultOutputBase.model_validate_json(args)
            clean_content, clean_sources = self._clean_output(
                content=result.content,
                sources=result.sources,
                documents=documents,
            )

            self.content.send(clean_content)
            self.sources.send(clean_sources)
            return

        else:
            raise Exception(f"Unexpected model finish reason {llm_response_type}")

    def _get_output_final_result_request(
        self,
        chat_history: list[MessageTypes],
        llm: LLM,
    ) -> ChatCompletionRequest:
        model_supports_tools = llm.check_model_can_support_tools()

        if model_supports_tools:
            if self._schema_is_string():

                class OutputFinalResultOutputWithSchema(BaseModel):
                    content: Annotated[
                        Any,
                        Field(
                            json_schema_extra=pydantic_core.to_jsonable_python(
                                self.response_schema
                            ),
                        ),
                    ]
                    sources: list[FinalResultSource] | None = None

                response_model = OutputFinalResultOutputWithSchema
            else:
                response_model = Analyzer.OutputFinalResultOutputString

            f = BaseChatFunction(
                name="output_result",
                description="Use this to output your response to the user. Content is a required field so always include it",
                parameters=response_model.model_json_schema(),
            )

            output_final_result_chat_request = ChatCompletionRequest(
                messages=chat_history,
                tools=[
                    BaseChatTool(
                        type="function",
                        function=f,
                    )
                ],
                tool_choice=ToolChoice(function=FunctionCall(name=f.name)),
            )

            return output_final_result_chat_request

        else:
            output_final_result_chat_request = ChatCompletionRequest(
                messages=chat_history,
                stop=["\n### Human"],
            )

            return output_final_result_chat_request

    def _clean_output(
        self,
        content: Any,
        sources: list[FinalResultSource] | None,
        documents: list[SearchResult],
    ) -> tuple[Any, list[Source]]:
        source_index = 1
        output_sources: list[Source] = []
        output_content = json.dumps(content, indent=4)

        if sources:
            for output_source in sources:
                for i, search_result in enumerate(documents):
                    if f"source_{i + 1}" == output_source.name:
                        output_sources.append(
                            Source(index=source_index, uri=(search_result.path or ""))
                        )
                        output_content = output_content.replace(
                            f"(source_{i + 1})", f"({source_index})"
                        ).replace(f"source_{i + 1}", f"({source_index})")
                        source_index += 1
                        break

        # clear citations that weren't matched with a search result
        output_content = re.sub(
            r" ?(\(source_[0-9?]{0,3}\))|(source_[0-9?]{0,3})", "", output_content
        )

        return (json.loads(output_content), output_sources)

    def _fix_json_escaping(self, content: str) -> str:
        sources_key_start = content.find('"sources"')

        content_key_start = content.find('"content"')
        content_key_end = content_key_start + len('"content"')

        # maybe there is a "sources" string in the content, so do a reverse search
        if sources_key_start > content_key_start:
            sources_key_start = content.rfind('"sources"')

        content_start = content.find('"', content_key_end) + 1
        if sources_key_start < content_key_start:
            content_end = content.rfind('"')
        else:
            content_end = content[: sources_key_start - 1].rfind('"', content_key_start)

        fixed_content = reduce(
            lambda content, patterns: re.sub(patterns[0], patterns[1], content),
            [
                (r'(?<!\\)"', r'\\"'),
                ("\x08", r"\\b"),
                (r"\f", r"\\f"),
                (r"\n", r"\\n"),
                (r"\r", r"\\r"),
                (r"\t", r"\\t"),
                (r'(?<!\\)(\\\\)*\\(?![\\"/bfnrtu])', r"\\\\"),
            ],
            content[content_start:content_end],
        )

        final_double_quote = content.rfind('"')
        content = content[:final_double_quote] + content[final_double_quote:].replace(
            ",", ""
        )

        return content[:content_start] + fixed_content + content[content_end:]
