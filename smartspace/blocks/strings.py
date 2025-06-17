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
    description="Combines two lists or strings into one. Joins data by appending the second input to the first. Use this to merge collections or text.",
    icon="fa-plus",
    obsolete=True,
    label="concatenate, join, merge, combine, append data",
    deprecated_reason="This block will be deprecated in a future version. Use Join instead.",
    use_instead="Join",
)
class Concat(Block, Generic[SequenceT]):
    @step(output_name="result")
    async def concat(self, a: SequenceT, b: SequenceT) -> SequenceT:
        return a + b  # type: ignore
