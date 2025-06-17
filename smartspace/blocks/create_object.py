from typing import Any

from smartspace.core import (
    Block,
    metadata,
    step,
)
from smartspace.enums import BlockCategory


@metadata(
    description="Combines multiple inputs into a single object. Each input becomes a key-value pair in the resulting object. Use this to structure data.",
    category=BlockCategory.MISC,
    icon="fa-cube",
    label="create object, build dictionary, structure data, key-value, aggregate",
)
class CreateObject(Block):
    @step(output_name="object")
    async def build(self, **properties: Any) -> dict[str, Any]:
        return properties
