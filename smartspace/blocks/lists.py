from typing import Annotated, Any, Generic, TypeVar

from more_itertools import flatten

from smartspace.core import (
    Block,
    ChannelEvent,
    Config,
    InputChannel,
    Metadata,
    OperatorBlock,
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
SequenceT = TypeVar("SequenceT", bound=list[Any] | str)


@metadata(
    category=BlockCategory.FUNCTION,
    description="Transforms each item in a list using a configured operation. Processes all items in parallel and returns transformed results. Use this to apply functions to collections.",
    icon="fa-project-diagram",
    label="map, transform items, process list, apply function, iterate collection",
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
    description="Collects data from a channel and outputs them as a list once the channel closes.",
    icon="fa-boxes",
    label="collect list, gather items, accumulate data, assemble collection, aggregate entries",
    obsolete=True,
    deprecated_reason="This block has been deprecated..",
)
class Collect(OperatorBlock, Generic[ItemT]):
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


@metadata(
    category=BlockCategory.FUNCTION,
    description="Counts the number of items in a list. Returns the total count as an integer. Use this to get collection size for validation or processing.",
    icon="fa-sort-numeric-up",
    label="count, list length, size, total items, number elements",
)
class Count(OperatorBlock):
    @step(output_name="output")
    async def count(self, items: list[Any]) -> int:
        return len(items)


@metadata(
    category=BlockCategory.FUNCTION,
    description="Outputs each item from a list individually. Sends items sequentially to enable downstream processing. Use this to iterate through collections.",
    icon="fa-ellipsis-h	",
    label="for each, iterate, loop list, process each, step through",
)
class ForEach(OperatorBlock, Generic[ItemT]):
    item: OutputChannel[ItemT]

    @step()
    async def foreach(self, items: list[ItemT]):
        for item in items:
            self.item.send(item)

        self.item.close()


@metadata(
    category=BlockCategory.FUNCTION,
    description="Joins a list of strings using the configured separator and outputs the resulting string.",
    icon="fa-link",
    label="join strings, concatenate text, combine strings, merge text, connect strings",
    obsolete=True,
    use_instead="Join",
    deprecated_reason="This block will be deprecated in a future version. Use Join instead.",
)
class JoinStrings(Block):
    separator: Annotated[str, Config(), Metadata(description="Text separator to join strings with.")] = ""

    @step(output_name="output")
    async def join(self, strings: list[str]) -> str:
        return self.separator.join(strings)


@metadata(
    category=BlockCategory.FUNCTION,
    description="Divides text into parts using a separator character. Returns list of substrings for further processing. Use this to parse structured text.",
    icon="fa-cut",
    label="split string, divide text, parse text, tokenize, break apart",
)
class SplitString(Block):
    separator: Annotated[str, Config(), Metadata(description="Text separator to split string on.")] = "\n"
    include_separator: Annotated[bool, Config(), Metadata(description="Include separator at end of each part.")] = False

    @step(output_name="output")
    async def split(self, string: str) -> list[str]:
        results = string.split(self.separator)

        if self.include_separator:
            results = [r + self.separator for r in results[:-1]] + [results[-1]]

        return results


@metadata(
    category=BlockCategory.FUNCTION,
    description="Extracts a portion of a list or string using start and end positions. Returns subset of original data. Use this for pagination or partial processing.",
    icon="fa-cut",
    label="slice, extract portion, get segment, subset, partial data",
)
class Slice(Block):
    start: Annotated[int, Config(), Metadata(description="Starting index for slice operation.")] = 0
    end: Annotated[int, Config(), Metadata(description="Ending index for slice operation.")] = 0

    @step(output_name="items")
    async def slice(self, items: list[Any] | str) -> list[Any] | str:
        return items[self.start : self.end]


firstItemT = TypeVar("firstItemT")


@metadata(
    category=BlockCategory.FUNCTION,
    description="Extracts the first item from a list. Returns the initial element for further processing. Use this to get the primary result from collections.",
    icon="fa-arrow-alt-circle-left",
    label="first, initial item, head element, primary result, get first",
)
class First(OperatorBlock, Generic[firstItemT]):
    @step(output_name="item")
    async def first(self, items: list[firstItemT]) -> firstItemT:
        return items[0]


@metadata(
    category=BlockCategory.FUNCTION,
    description="Converts nested lists into a single flat list. Removes one level of nesting from data structures. Use this to simplify complex collections.",
    icon="fa-compress",
    label="flatten, merge nested, combine arrays, unnest, simplify structure",
)
class Flatten(OperatorBlock):
    @step(output_name="list")
    async def flatten(self, lists: list[list[Any]]) -> list[Any]:
        return list(flatten(lists))
