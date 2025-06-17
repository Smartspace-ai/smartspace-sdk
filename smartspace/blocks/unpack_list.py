from typing import Any

from smartspace.core import (
    Block,
    Output,
    metadata,
    step,
)
from smartspace.enums import BlockCategory


@metadata(
    description="Separates list items into individual outputs. Each item goes to its corresponding output port. Use this to break down lists for parallel processing.",
    category=BlockCategory.MISC,
    icon="fa-th-list",
    label="unpack list, distribute items, separate elements, spread array, decompose",
)
class UnpackList(Block):
    items: list[Output[Any]]

    @step()
    async def unpack(self, list: list[Any]):
        for i, v in enumerate(list):
            if len(self.items) > i:
                self.items[i].send(v)
