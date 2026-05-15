from typing import Annotated, Any

from smartspace.core import Block, Config, Metadata, Output, State, metadata, step
from smartspace.enums import BlockCategory


@metadata(
    category=BlockCategory.CONTROL,
    icon="fa-gauge-high",
    label="limit, counter, threshold, gate, limiter",
    description=(
        "Routes incoming items based on a configurable count limit. "
        "Emits to `under_limit` until the limit is reached; afterwards emits to `reached_limit`."
    ),
)
class Limit(Block):
    limit: Annotated[
        int,
        Config(),
        Metadata(description="Maximum number of items to pass through under_limit"),
    ] = 5

    count: Annotated[int, State()] = 0

    under_limit: Output[Any]
    reached_limit: Output[Any]

    @step()
    async def route(self, item: Any):
        self.count += 1

        if self.count < self.limit:
            self.under_limit.send(item)
        else:
            self.reached_limit.send(item)
