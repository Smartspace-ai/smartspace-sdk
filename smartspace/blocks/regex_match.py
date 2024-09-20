import re
from typing import Annotated

from smartspace.core import Block, Config, metadata, step
from smartspace.enums import BlockCategory


@metadata(
    category=BlockCategory.FUNCTION,
    description="regex-based pattern matching on a string input, returning a list of all matches found.",
)
class RegexMatch(Block):
    """
    Input:
        1. a string input
        2. a regex expression
    Output: a list of match results of a regex expression
    """

    regex: Annotated[str, Config()] = (
        r".*"  # Default pattern to match the entire string
    )

    @step(output_name="result")
    async def regex_match(self, input_strings: str) -> list[str]:
        try:
            pattern = re.compile(self.regex)
            match = pattern.findall(input_strings)
            if len(match) == 0:
                return ["No match found"]
            return match
        except Exception as e:
            error_message = f"Error: {e}"
            return [error_message]
