from typing import Any

from smartspace.core import (
    Block,
    metadata,
    step,
)
from smartspace.enums import BlockCategory


@metadata(
    description="Takes in inputs and creates a list containing the inputs",
    category=BlockCategory.MISC,
)
class CreateList(Block):
    @step(output_name="list")
    async def build(self, *items: Any) -> list[Any]:
        return list(items)
