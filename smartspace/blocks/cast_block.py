import json
from typing import Any, Generic, TypeVar, cast

from pydantic import BaseModel, ConfigDict

from smartspace.core import (
    Block,
    GenericSchema,
    metadata,
    step,
)
from smartspace.enums import BlockCategory

ItemT = TypeVar("ItemT")


@metadata(
    description="Takes in any input and will attempt to convert the input to the specified schema",  # Fixed typo
    category=BlockCategory.MISC,
)
class Cast(Block, Generic[ItemT]):
    schema: GenericSchema[ItemT]

    @step(output_name="result")
    async def cast(self, item: Any) -> ItemT:
        if "type" not in self.schema:
            return item

        return self._cast(item, self.schema)

    def _cast(self, item: Any, schema: dict[str, Any]) -> Any:
        if "type" not in schema:
            return item

        if schema["type"] == "array":
            return cast(ItemT, [self._cast(i, schema["items"]) for i in item])

        if schema["type"] == "object":
            if isinstance(item, str):
                item = json.loads(item)

            if len(schema) == 1:
                return item

            class M(BaseModel):
                model_config = ConfigDict(
                    json_schema_extra=schema,
                )

            if isinstance(item, dict):
                return M.model_validate(item)
            elif isinstance(item, str):
                return M.model_validate_json(item)
            else:
                raise ValueError(f"Cannot cast type '{type(item)}' to object")

        elif schema["type"] == "string":
            if isinstance(item, str):
                return item
            else:
                return json.dumps(item, indent=2)

        elif schema["type"] == "number":
            if isinstance(item, (int, float)):
                return item
            else:
                try:
                    return float(item)
                except (TypeError, ValueError) as e:
                    raise ValueError(f"Cannot convert '{item}' to float.") from e
        else:
            return item
