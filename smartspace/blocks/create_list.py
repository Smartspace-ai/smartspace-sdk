from typing import Any

from smartspace.core import (
    Block,
    metadata,
    step,
)
from smartspace.enums import BlockCategory


@metadata(
    description="Takes in inputs and creates a list containing the inputs.",
    category=BlockCategory.MISC,
    icon="fa-list-ul",
    label="create list, build list, construct list, form list, make list",
)
class CreateList(Block):
    @step(output_name="list")
    async def build(self, *items: Any) -> list[Any]:
        return list(items)
