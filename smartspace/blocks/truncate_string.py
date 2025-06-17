from typing import Annotated

from litellm.utils import decode, encode

from smartspace.core import Block, Config, Metadata, metadata, step
from smartspace.enums import BlockCategory


@metadata(
    category=BlockCategory.FUNCTION,
    description="Shortens text to fit within a token limit for AI models. Cuts text at the token boundary while preserving beginning content. Use this to ensure text fits model constraints.",
    icon="fa-cut",
    label="truncate, shorten text, token limit, trim text, model constraints",
)
class StringTruncator(Block):
    max_token: Annotated[int, Config(), Metadata(description="Maximum number of tokens to keep.")] = 100
    model_name: Annotated[str, Config(), Metadata(description="Tokenizer model for token counting.")] = "gpt-3.5-turbo"

    @step(output_name="result")
    async def truncate_string(self, input_strings: str) -> str:
        tokens = encode(model=self.model_name, text=input_strings)

        if len(tokens) <= self.max_token:
            return input_strings

        # Truncate the tokens
        truncated_tokens = tokens[: self.max_token]

        # Decode the truncated tokens back to a string
        truncated_string = decode(model=self.model_name, tokens=truncated_tokens)

        return truncated_string
