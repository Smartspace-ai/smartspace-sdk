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
    description="Checks the output schemas of the options and sends the input to the first option that matches",
    category=BlockCategory.MISC,
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
