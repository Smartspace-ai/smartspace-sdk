import json
from typing import Annotated, Any, Generic, TypeVar, cast

from jinja2 import BaseLoader, Environment
from pydantic import BaseModel, ConfigDict, ValidationError
from smartspace.core import (
    Block,
    Config,
    GenericSchema,
    Output,
    metadata,
    step,
)


@metadata(category={"name": "Misc"})
class StringTemplate(Block):
    template: Annotated[str, Config()]

    @step(output_name="string")
    async def build(self, **inputs: Any) -> str:
        template = Environment(loader=BaseLoader()).from_string(self.template)
        return template.render(**inputs)


@metadata(category={"name": "Misc"})
class CreateObject(Block):
    @step(output_name="object")
    async def build(self, **properties: Any) -> dict[str, Any]:
        return properties


@metadata(category={"name": "Misc"})
class CreateList(Block):
    @step(output_name="list")
    async def build(self, *items: Any) -> list[Any]:
        return list(items)


@metadata(category={"name": "Misc"})
class UnpackObject(Block):
    properties: dict[str, Output[dict[str, Any]]]

    @step()
    async def unpack(self, object: dict[str, Any]):
        for name, value in object.items():
            if name in self.properties:
                self.properties[name].send(value)


@metadata(category={"name": "Misc"})
class UnpackList(Block):
    items: list[Output[Any]]

    @step()
    async def unpack(self, list: list[Any]):
        for i, v in enumerate(list):
            if len(self.items) > i:
                self.items[i].send(v)


ItemT = TypeVar("ItemT")


class TypeSwitchOption(Generic[ItemT]):
    schema: GenericSchema[ItemT]
    option: Output[ItemT]


@metadata(category={"name": "Misc"})
class TypeSwitch(Block):
    options: list[TypeSwitchOption]

    @step(output_name="result")
    async def switch(self, item: Any):
        for option in self.options:

            class M(BaseModel):
                model_config = ConfigDict(
                    json_schema_extra=option.schema,
                )

            try:
                option.option.send(M.model_validate(item, strict=True))
            except ValidationError:
                ...


@metadata(category={"name": "Misc"})
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

            class M(BaseModel):
                model_config = ConfigDict(
                    json_schema_extra=schema,
                )

            if isinstance(item, dict):
                return M.model_validate(item)
            elif isinstance(item, str):
                return M.model_validate_json(item)
            else:
                raise ValueError(f"Can not cast type '{type(item)}' to object")

        elif schema["type"] == "string":
            if isinstance(item, str):
                return item
            else:
                return json.dumps(item, indent=2)

        elif schema["type"] == "number":
            if isinstance(item, (int, float)):
                return item
            else:
                return float(item)
        else:
            return item
