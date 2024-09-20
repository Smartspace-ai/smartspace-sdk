from typing import Annotated

from litellm.utils import decode, encode

from smartspace.core import Block, Config, metadata, step
from smartspace.enums import BlockCategory


@metadata(
    category=BlockCategory.FUNCTION,
    description="takes in a string input and truncates it given a token limit",
)
class StringTruncator(Block):
    max_token: Annotated[int, Config()] = 100  # default token limit
    model_name: Annotated[str, Config()] = "gpt-3.5-turbo"  # default model

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
