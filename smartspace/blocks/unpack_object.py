from typing import Any

from smartspace.core import (
    Block,
    Output,
    metadata,
    step,
)
from smartspace.enums import BlockCategory


@metadata(
    description="Separates object properties into individual outputs. Each property value goes to its corresponding output port. Use this to break down objects for parallel processing.",
    category=BlockCategory.MISC,
    icon="fa-th-large",
    label="unpack object, extract properties, decompose dictionary, spread object, distribute",
)
class UnpackObject(Block):
    properties: dict[str, Output[dict[str, Any]]]

    @step()
    async def unpack(self, object: dict[str, Any]):
        for name, value in object.items():
            if name in self.properties:
                self.properties[name].send(value)
