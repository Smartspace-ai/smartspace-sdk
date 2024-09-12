from typing import Annotated, Any

from more_itertools import flatten

from smartspace.core import (
    Block,
    Config,
    InputConfig,
    Output,
    State,
    Tool,
    callback,
    metadata,
    step,
)
from smartspace.enums import BlockCategory


@metadata(
    category=BlockCategory.FUNCTION,
    description="Loops through each item in the items input and sends them to the configured tool. Once all items have been processed, outputs the resulting list",
)
class Map(Block):
    class Operation(Tool):
        def run(self, item: Any) -> Any: ...

    run: Operation

    results: Output[list[Any]]

    count: Annotated[
        int,
        State(
            step_id="map",
            input_ids=["items"],
            default_value=0,
        ),
    ]

    results_state: Annotated[
        list[Any],
        State(
            step_id="map",
            input_ids=["items"],
            default_value=[],
        ),
    ]

    @step()
    async def map(self, items: list[Any]):
        if len(items) == 0:
            self.results.emit([])
            return

        self.results_state = [None] * len(items)
        self.count = len(items)
        for i, item in enumerate(items):
            self.run.call(item).then(lambda result: self.collect(result, i))

    @callback()
    async def collect(
        self,
        result: Any,
        index: int,
    ):
        self.results_state[index] = result
        self.count -= 1

        if self.count == 0:
            self.results.emit(self.results_state)


@metadata(
    category=BlockCategory.FUNCTION,
    description="Collects data and outputs as a list.\nOnce 'count' items have been received it will output the items in a list",
)
class Collect(Block):
    items: Output[list[Any]]

    items_state: Annotated[
        list[Any],
        State(
            step_id="collect",
            input_ids=["count"],
            default_value=[],
        ),
    ]

    @step()
    async def collect(
        self,
        item: Any,
        count: Annotated[int, InputConfig(sticky=True)],
    ):
        self.items_state.append(item)

        if len(self.items_state) == count:
            self.items.emit(self.items_state)
            self.items_state = []


@metadata(category=BlockCategory.FUNCTION)
class Count(Block):
    @step(output_name="output")
    async def count(self, items: list[Any]) -> int:
        return len(items)


@metadata(
    category=BlockCategory.FUNCTION,
    description="Loops through a list of items and outputs them one at a time",
)
class ForEach(Block):
    item: Output[Any]

    @step()
    async def foreach(self, items: list[Any]):
        for item in items:
            self.item.emit(item)


@metadata(
    category=BlockCategory.FUNCTION,
    description="Joins a list of strings using the configured separator and outputs the resulting string",
)
class JoinStrings(Block):
    separator: Config[str] = ""

    @step(output_name="output")
    async def join(self, strings: list[str]) -> str:
        return self.separator.join(strings)


@metadata(
    category=BlockCategory.FUNCTION,
    description="Splits a string using the configured separator and outputs a list of the substrings",
)
class SplitString(Block):
    separator: Config[str] = "\n"
    include_separator: Config[bool] = False

    @step(output_name="output")
    async def split(self, string: str) -> list[str]:
        results = string.split(self.separator)

        if self.include_separator:
            results = [r + self.separator for r in results[:-1]] + [results[-1]]

        return results


@metadata(
    category=BlockCategory.FUNCTION,
    description="Slices a list or string using the configured start and end indexes",
)
class Slice(Block):
    start: Config[int] = 0
    end: Config[int] = 0

    @step(output_name="items")
    async def slice(self, items: list[Any] | str) -> list[Any] | str:
        return items[self.start : self.end]


@metadata(
    category=BlockCategory.FUNCTION,
    description="Gets the first item from a list",
)
class First(Block):
    @step(output_name="item")
    async def first(self, items: list[Any]) -> Any:
        return items[0]


@metadata(
    category=BlockCategory.FUNCTION,
    description="Flattens a list of lists into a single list",
)
class Flatten(Block):
    @step(output_name="list")
    async def flatten(self, lists: list[list[Any]]) -> list[Any]:
        return list(flatten(lists))
