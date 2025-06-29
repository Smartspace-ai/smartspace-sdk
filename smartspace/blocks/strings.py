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
    label="concatenate strings, join strings, merge lists, combine text, append strings",
)
class Concat(Block, Generic[SequenceT]):
    @step(output_name="result")
    async def concat(self, a: SequenceT, b: SequenceT) -> SequenceT:
        # Handle empty lists - don't add them
        if isinstance(a, list) and isinstance(b, list):
            if not a:  # a is empty
                return b
            if not b:  # b is empty
                return a
            # Both lists have content, concatenate normally
            return a + b  # type: ignore
        
        # For strings or mixed types, use normal concatenation
        return a + b  # type: ignore
