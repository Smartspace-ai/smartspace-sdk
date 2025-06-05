from typing import Any
import json
import re

from smartspace.core import (
    Block,
    metadata,
    step,
)
from smartspace.enums import BlockCategory


@metadata(
    description="Merges multiple dictionaries into a single object. Accepts only dicts and combines all key-value pairs into one dictionary.",
    category=BlockCategory.MISC,
    icon="fa-cube",
    label="merge objects, combine dictionaries, build object, aggregate key-value pairs",
)
class MergeObjects(Block):
    @step(output_name="object")
    async def build(self, *objects: dict[str, Any]) -> dict[str, Any]:
        merged_object = {}
        for obj in objects:
            merged_object.update(obj)
        return merged_object



