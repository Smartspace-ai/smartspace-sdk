from typing import Annotated, Any, Generic, TypeVar

from more_itertools import flatten

from smartspace.core import (
    Block,
    ChannelEvent,
    Config,
    InputChannel,
    Output,
    OutputChannel,
    State,
    Tool,
    callback,
    metadata,
    step,
)
from smartspace.enums import BlockCategory, ChannelState

ItemT = TypeVar("ItemT")
ResultT = TypeVar("ResultT")


@metadata(
    category=BlockCategory.FUNCTION,
    description="Loops through each item in the items input and sends them to the configured tool. Once all items have been processed, outputs the resulting list",
)
class Map(Block, Generic[ItemT, ResultT]):
    class Operation(Tool):
        def run(self, item: ItemT) -> ResultT: ...

    run: Operation

    results: Output[list[ResultT]]

    count: Annotated[
        int,
        State(
            step_id="map",
            input_ids=["items"],
        ),
    ] = 0

    results_state: Annotated[
        list[Any],
        State(
            step_id="map",
            input_ids=["items"],
        ),
    ] = []

    @step()
    async def map(self, items: list[ItemT]):
        if len(items) == 0:
            self.results.send([])
            return

        self.results_state = [None] * len(items)
        self.count = len(items)
        for i, item in enumerate(items):
            await self.run.call(item).then(lambda result: self.collect(result, i))

    @callback()
    async def collect(
        self,
        result: ResultT,
        index: int,
    ):
        self.results_state[index] = result
        self.count -= 1

        if self.count == 0:
            self.results.send(self.results_state)


@metadata(
    category=BlockCategory.FUNCTION,
    description="Collects data from a channel and outputs them as a list once the channel closes",
)
class Collect(Block, Generic[ItemT]):
    items: Output[list[ItemT]]

    items_state: Annotated[
        list[ItemT],
        State(
            step_id="collect",
            input_ids=["item"],
        ),
    ] = []

    @step()
    async def collect(
        self,
        item: InputChannel[ItemT],
    ):
        if (
            item.state == ChannelState.OPEN
            and item.event == ChannelEvent.DATA
            and item.data
        ):
            self.items_state.append(item.data)

        if item.event == ChannelEvent.CLOSE:
            self.items.send(self.items_state)


class Count(Block):
    @step(output_name="output")
    async def count(self, items: list[Any]) -> int:
        return len(items)


@metadata(
    category=BlockCategory.FUNCTION,
    description="Loops through a list of items and outputs them one at a time",
)
class ForEach(Block, Generic[ItemT]):
    item: OutputChannel[ItemT]

    @step()
    async def foreach(self, items: list[ItemT]):
        for item in items:
            self.item.send(item)

        self.item.close()


@metadata(
    category=BlockCategory.FUNCTION,
    description="Joins a list of strings using the configured separator and outputs the resulting string",
)
class JoinStrings(Block):
    separator: Annotated[str, Config()] = ""

    @step(output_name="output")
    async def join(self, strings: list[str]) -> str:
        return self.separator.join(strings)


@metadata(
    category=BlockCategory.FUNCTION,
    description="Splits a string using the configured separator and outputs a list of the substrings",
)
class SplitString(Block):
    separator: Annotated[str, Config()] = "\n"
    include_separator: Annotated[bool, Config()] = False

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
    start: Annotated[int, Config()] = 0
    end: Annotated[int, Config()] = 0

    @step(output_name="items")
    async def slice(self, items: list[Any] | str) -> list[Any] | str:
        return items[self.start : self.end]

firstItemT = TypeVar("firstItemT")

@metadata(
    category=BlockCategory.FUNCTION,
    description="Gets the first item from a list",
)
class First(Block, Generic[firstItemT]):
    @step(output_name="item")
    async def first(self, items: list[firstItemT]) -> firstItemT:
        return items[0]


@metadata(
    category=BlockCategory.FUNCTION,
    description="Flattens a list of lists into a single list",
)
class Flatten(Block):
    @step(output_name="list")
    async def flatten(self, lists: list[list[Any]]) -> list[Any]:
        return list(flatten(lists))
