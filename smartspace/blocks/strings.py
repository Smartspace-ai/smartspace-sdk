from typing import Any, Generic, TypeVar

from smartspace.core import (
    Block,
    metadata,
    step,
)
from smartspace.enums import BlockCategory

SequenceT = TypeVar("SequenceT", bound=str | list[Any])


@metadata(
    category=BlockCategory.FUNCTION,
    description="Concatenates 2 lists or strings",
)
class Concat(Block, Generic[SequenceT]):
    @step(output_name="result")
    async def concat(self, a: SequenceT, b: SequenceT) -> SequenceT:
        return a + b  # type: ignore
