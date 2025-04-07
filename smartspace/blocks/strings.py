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
    icon="fa-plus",
    obsolete=True,
    label="concatenate strings, join strings, merge lists, combine text, append strings",
    deprecated_reason="This block will be deprecated in a future version. Use Join instead.",
    use_instead="Join",
)
class Concat(Block, Generic[SequenceT]):
    @step(output_name="result")
    async def concat(self, a: SequenceT, b: SequenceT) -> SequenceT:
        return a + b  # type: ignore
