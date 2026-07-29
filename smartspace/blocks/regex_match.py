import re
from typing import Annotated

from smartspace.core import Block, Config, Metadata, metadata, step
from smartspace.enums import BlockCategory, InputLanguage


@metadata(
    category=BlockCategory.TRANSFORM,
    description="Regex match or replace: if substitution string is empty, return list of matches; otherwise return replaced string.",
    icon="fa-text-width",
    label="regex match, regex replace, find and replace, pattern substitution, text extraction",
)
class RegexMatch(Block):
    """
    Performs a regex find-and-replace on the input string using the configured
    pattern and substitution string.
    """

    regex: Annotated[
        str,
        Config(),
        Metadata(
            language=InputLanguage.REGEX,
            description=(
                "Python regular expression (re module syntax), e.g. "
                r"\b(\w+)@(\w+\.\w+)\b."
                "\n"
                "Named groups are (?P<name>...); backreferences in "
                "replace_with are \\1 or \\g<name>. With replace_with empty "
                "the block returns the list of matches; otherwise the "
                "replaced string."
            ),
        ),
    ] = (
        r".*"  # Default pattern to match the entire string
    )
    replace_with: Annotated[
        str,
        Config(),
        Metadata(description="The string to replace each match with."),
    ] = ""

    @step(output_name="result")
    async def regex_match(
        self,
        input_string: Annotated[
            str,
            Metadata(description="The input text to match against or modify."),
        ],
    ) -> str | list[str]:
        try:
            pattern = re.compile(self.regex)
        except re.error as e:
            return [f"Error: {e}"] if self.replace_with == "" else f"Error: {e}"

        if self.replace_with == "":
            try:
                matches = pattern.findall(input_string)
                if len(matches) == 0:
                    return ["No match found"]
                return matches
            except Exception as e:
                return [f"Error: {e}"]
        else:
            try:
                substituted = pattern.sub(self.replace_with, input_string)
                return substituted
            except Exception as e:
                return f"Error: {e}"
