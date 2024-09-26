from typing import Any

from smartspace.core import (
    Block,
    Output,
    metadata,
    step,
)
from smartspace.enums import BlockCategory


@metadata(
    description="Takes in an object and sends each key-value pair to the corresponding output",
    category=BlockCategory.MISC,
)
class UnpackObject(Block):
    properties: dict[str, Output[dict[str, Any]]]

    @step()
    async def unpack(self, object: dict[str, Any]):
        for name, value in object.items():
            if name in self.properties:
                self.properties[name].send(value)
