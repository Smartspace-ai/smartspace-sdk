from typing import Annotated

from smartspace.core import Block, Config, Metadata, metadata, step
from smartspace.enums import BlockCategory


@metadata(
    description="Outputs a predefined dictionary object. Configure the object properties once and reuse across workflows. Use this for constant data structures.",
    category=BlockCategory.MISC,
    icon="fa-book",
    label="constant, dictionary, static object, fixed data, reusable",
)
class DictConst(Block):
    output: Annotated[dict, Config(), Metadata(description="Dictionary object to output.")]

    @step(output_name="output")
    async def build(self) -> dict:
        return self.output


@metadata(
    description="Outputs a predefined text string. Configure the text once and reuse across workflows. Use this for constant messages, labels, or template text.",
    category=BlockCategory.MISC,
    icon="fa-quote-right",
    label="constant, string, static text, fixed message, reusable",
)
class StringConst(Block):
    output: Annotated[str, Config(), Metadata(description="Text string to output.")]

    @step(output_name="output")
    async def build(self) -> str:
        return self.output


@metadata(
    description="Outputs a predefined number value. Configure the number once and reuse across workflows. Use this for thresholds, counters, or configuration values.",
    category=BlockCategory.MISC,
    icon="fa-hashtag",
    label="constant, number, static value, fixed integer, reusable",
)
class IntegerConst(Block):
    output: Annotated[int, Config(), Metadata(description="Integer number to output.")]

    @step(output_name="output")
    async def build(self) -> int:
        return self.output
