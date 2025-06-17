from typing import Generic, TypeVar

from smartspace.core import (
    Block,
    metadata,
    step,
)
from smartspace.enums import BlockCategory

ItemT = TypeVar("ItemT")


@metadata(
    description="Adds a single item to the end of a list. Creates a new list with the original items plus the appended item. Use this to build collections incrementally.",
    category=BlockCategory.MISC,
    icon="fa-plus",
    label="append, add item, extend list, build collection, accumulate",
)
class Append(Block, Generic[ItemT]):
    @step(output_name="items")
    async def build(self, items: list[ItemT], item: ItemT) -> list[ItemT]:
        items.append(item)
        return items
