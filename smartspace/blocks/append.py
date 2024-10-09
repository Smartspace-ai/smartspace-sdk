from typing import Generic, TypeVar

from smartspace.core import (
    Block,
    metadata,
    step,
)
from smartspace.enums import BlockCategory

ItemT = TypeVar("ItemT")


@metadata(
    description="Appends item to items and output resulting list",
    category=BlockCategory.MISC,
)
class Append(Block, Generic[ItemT]):
    @step(output_name="items")
    async def build(self, items: list[ItemT], item: ItemT) -> list[ItemT]:
        items.append(item)
        return items
