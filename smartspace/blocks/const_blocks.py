from typing import Annotated

from smartspace.core import Block, Config, metadata, step
from smartspace.enums import BlockCategory


@metadata(
    description="Takes a dictionary as config and outputs it.",
    category=BlockCategory.MISC,
)
class DictConst(Block):
    output: Annotated[dict, Config()]

    @step(output_name="output")
    async def build(self) -> dict:
        return self.output


@metadata(
    description="Takes a string as config and outputs it.",
    category=BlockCategory.MISC,
)
class StringConst(Block):
    output: Annotated[str, Config()]

    @step(output_name="output")
    async def build(self) -> str:
        return self.output


@metadata(
    description="Takes an integer as config and outputs it.",
    category=BlockCategory.MISC,
)
class IntegerConst(Block):
    output: Annotated[int, Config()]

    @step(output_name="output")
    async def build(self) -> int:
        return self.output
