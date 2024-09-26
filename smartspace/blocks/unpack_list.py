from typing import Any

from smartspace.core import (
    Block,
    Output,
    metadata,
    step,
)
from smartspace.enums import BlockCategory


@metadata(
    description="Takes in a list and sends each item to the corresponding output",
    category=BlockCategory.MISC,
)
class UnpackList(Block):
    items: list[Output[Any]]

    @step()
    async def unpack(self, list: list[Any]):
        for i, v in enumerate(list):
            if len(self.items) > i:
                self.items[i].send(v)
