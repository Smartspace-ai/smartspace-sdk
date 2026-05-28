from typing import Annotated, Any

import jmespath
from jmespath.exceptions import JMESPathError

from smartspace.core import Block, BlockError, Config, Metadata, Output, metadata, step
from smartspace.enums import BlockCategory


@metadata(
    category=BlockCategory.TRANSFORM,
    icon="fa-shuffle",
    label="transform, jmespath, reshape, project, map, select, filter, json query, dynamic inputs, multi input",
    description=(
        "Transforms, filters, and reshapes JSON data using a JMESPath expression. "
        "Accepts dynamic inputs: each connected input pin becomes a top-level key "
        "in the document the expression sees. Example: with pins `user` and `items` "
        "wired in, the expression `{name: user.name, count: length(items)}` returns "
        "`{\"name\": ..., \"count\": ...}`. Unlike the JSONPath-based Get block, "
        "JMESPath can construct new objects, apply filters (`[?type=='admin']`), "
        "slice, pipe, and call built-in functions."
    ),
)
class Transform(Block):
    expression: Annotated[
        str,
        Config(),
        Metadata(
            description=(
                "JMESPath expression to evaluate against an object whose keys are "
                "the names of the connected input pins. See https://jmespath.org/ for syntax."
            )
        ),
    ] = "@"

    result: Output[Any]

    @step()
    async def transform(self, **inputs: Any):
        try:
            compiled = jmespath.compile(self.expression)
        except JMESPathError as e:
            raise BlockError(f"Invalid JMESPath expression {self.expression!r}: {e}")

        try:
            value = compiled.search(inputs)
        except JMESPathError as e:
            raise BlockError(
                f"JMESPath evaluation failed for expression {self.expression!r}: {e}"
            )

        self.result.send(value)
