from typing import Any

from smartspace.core import (
    Block,
    metadata,
    step,
)
from smartspace.enums import BlockCategory


@metadata(
    category=BlockCategory.FUNCTION,
    description="Concatenates 2 lists or strings",
)
class Concat(Block):
    @step(output_name="result")
    async def concat(self, a: str | list[Any], b: str | list[Any]) -> str | list[Any]:
        if (isinstance(a, str) and isinstance(b, list)) or (
            isinstance(a, list) and isinstance(b, str)
        ):
            raise Exception("a and b must either both be strings or both be lists")

        return a + b  # type: ignore
