from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, ValidationError

from smartspace.core import (
    Block,
    GenericSchema,
    Output,
    metadata,
    step,
)
from smartspace.enums import BlockCategory

ItemT = TypeVar("ItemT")


class TypeSwitchOption(Generic[ItemT]):
    schema: GenericSchema[ItemT]
    option: Output[ItemT]


@metadata(
    description="Routes input data to different paths based on data type. Checks input against schemas and sends to the first matching option. Use this for conditional processing.",
    category=BlockCategory.MISC,
    icon="fa-random",
    label="type routing, conditional logic, data branching, schema matching, switch",
)
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
