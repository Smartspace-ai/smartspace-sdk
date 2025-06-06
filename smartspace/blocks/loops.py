from typing import Annotated, Any, Generic, TypeVar

from smartspace.core import (
    Block,
    ChannelEvent,
    Config,
    InputChannel,
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

@metadata(
    category=BlockCategory.FUNCTION,
    description="Loops through each item in the items input and sends them to the configured tool. Once all items have been processed, outputs the resulting list",
    icon="fa-project-diagram",
    label="map function, transform items, process list, iterate collection, apply function to list",
)
class Map(Block, Generic[ItemT, ResultT]):
    class Operation(Tool):
        def run(self, item: ItemT) -> ResultT: ...

    run: Operation

    results: Output[list[ResultT]]

    synchronous: Annotated[bool, Config()] = False

    items: Annotated[
        list[ItemT],
        State(
            step_id="map",
            input_ids=["items"],
        ),
    ] = []

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

        self.items = items
        self.results_state = [None] * len(items)
        self.count = len(items)
        if self.synchronous:
            await self.run.call(items[0]).then(lambda result: self.collect(result, 0))
        else:
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
        elif self.synchronous:
            i = len(self.items) - self.count
            await self.run.call(self.items[i]).then(
                lambda result: self.collect(result, i)
            )

@metadata(
    category=BlockCategory.FUNCTION,
    description="Collects data from a channel and outputs them as a list once the channel closes.",
    icon="fa-boxes",
    label="collect list, gather items, accumulate data, assemble collection, aggregate entries",
    obsolete=True,
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
    description="Loops through a list of items and outputs them one at a time",
    icon="fa-ellipsis-h\t",
    label="for each, iterate items, loop through list, process each item, step through collection",
)
class ForEach(OperatorBlock, Generic[ItemT]):
    item: OutputChannel[ItemT]

    @step()
    async def foreach(self, items: list[ItemT]):
        for item in items:
            self.item.send(item)

        self.item.close()
