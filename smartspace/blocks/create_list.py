from typing import Any

from smartspace.core import (
    Block,
    metadata,
    step,
)
from smartspace.enums import BlockCategory


@metadata(
    description="Combines multiple inputs into a single list. Each input becomes an item in the resulting list. Use this to group related values together.",
    category=BlockCategory.MISC,
    icon="fa-list-ul",
    label="create list, combine inputs, group values, build array, aggregate",
)
class CreateList(Block):
    @step(output_name="list")
    async def build(self, *items: Any) -> list[Any]:
        return list(items)
