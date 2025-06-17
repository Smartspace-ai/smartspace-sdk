import re
from typing import Annotated

from smartspace.core import Block, Config, Metadata, metadata, step
from smartspace.enums import BlockCategory


@metadata(
    category=BlockCategory.FUNCTION,
    description="Finds text patterns using regular expressions. Returns all matches found in the input text as a list. Use this to extract structured data from text.",
    icon="fa-text-width",
    label="regex, pattern matching, text extraction, regular expression, find patterns",
)
class RegexMatch(Block):
    """
    Input:
        1. a string input
        2. a regex expression
    Output: a list of match results of a regex expression
    """

    regex: Annotated[str, Config(), Metadata(description="Regular expression pattern to match.")] = (
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
