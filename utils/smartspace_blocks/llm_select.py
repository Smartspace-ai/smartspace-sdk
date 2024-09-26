from typing import Annotated, cast

from injector import inject
from litellm import Choices
from smartspace.core import (
    Config,
    Tool,
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
    ChatCompletionRequest,
    ModelConfig,
    UserMessageContentList,
)
from app.integrations.tokenization.tokenization_factory import (
    TokenizationServiceFactory,
)


@metadata(category=BlockCategory.AGENT)
class LLMSelect(WorkSpaceBlock):
    class Option(Tool):
        description: Annotated[str, Config()]

        def run(self, run: list[ContentItem] | str): ...

    llm_config: ModelConfig
    use_thread_history: Annotated[bool, Config()]

    options: dict[str, Option]

    @inject
    def __init__(
        self,
        llm_factory: LLMFactory,
        blob_service: BlobService,
        tokenization_service_factory: TokenizationServiceFactory,
    ):
        super().__init__()

        self.llm_factory = llm_factory
        self.blob_service = blob_service
        self.tokenization_service_factory = tokenization_service_factory

    @step()
    async def chat(self, message: list[ContentItem] | str):
        llm = await self.llm_factory.create_llm_from_model(self.llm_config)
        tokenization_service = self.tokenization_service_factory.create(llm.config)

        pre_prompt = (
            f"{self.llm_config.pre_prompt}\n"
            if self.llm_config.pre_prompt is not None
            else ""
        )
        pre_prompt += (
            "Given the user message below, please select one of the following options\n"
        )
        pre_prompt += "\n".join(
            [f"{name}: {option.description}" for name, option in self.options.items()]
        )
        history = await prepare_chat_history(
            pre_prompt=pre_prompt,
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

        option_tokens = {
            option: tokenization_service.encode_tokens(option)
            for option in self.options.keys()
        }

        if llm.settings is None:
            raise Exception("LLM settings is unexpectedly None")

        # llm.settings.logit_bias = {o: 100 for o in flatten(option_tokens.values())}
        llm.settings.max_tokens = max([len(o) for o in option_tokens.values()])

        request = ChatCompletionRequest(
            messages=history,
        )

        request = llm.remove_excess_tokens_chat_request(chat_request=request)
        llm_response = await llm.create_chat_completion(
            request=request,
            step_name=self.__class__.__name__,
        )

        choice = cast(Choices, llm_response.choices[0])
        content = choice.message.content.strip()

        # search through options in descending order of length and look for a match. Sometimes the LLM might return the name of the option twice, so we are checking startswith
        for option_name, option in sorted(
            self.options.items(), key=lambda x: len(x[0]), reverse=True
        ):
            if content.startswith(option_name):
                await option.call(message)
                return

        raise Exception("LLM response did not match any of the options")
