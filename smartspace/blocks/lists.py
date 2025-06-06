from typing import Annotated, Any, Generic, TypeVar

from more_itertools import flatten

from smartspace.core import (
    Block,
    Config,
    OperatorBlock,
    Output,
    State,
    metadata,
    step,
)
from smartspace.enums import BlockCategory

ItemT = TypeVar("ItemT")
ResultT = TypeVar("ResultT")
SequenceT = TypeVar("SequenceT", bound=list[Any] | str)
firstItemT = TypeVar("firstItemT")


@metadata(
    category=BlockCategory.FUNCTION,
    icon="fa-sort-numeric-up",
    label="count items, list length, item count, size of list, total elements",
)
class Count(OperatorBlock):
    @step(output_name="output")
    async def count(self, items: list[Any]) -> int:
        return len(items)


@metadata(
    category=BlockCategory.FUNCTION,
    description="Joins a list of strings using the configured separator and outputs the resulting string.",
    icon="fa-link",
    label="join strings, concatenate text, combine strings, merge text, connect strings",
)
class JoinStrings(Block):
    separator: Annotated[str, Config()] = ""

    @step(output_name="output")
    async def join(self, strings: list[str]) -> str:
        return self.separator.join(strings)


@metadata(
    category=BlockCategory.FUNCTION,
    description="Splits a string using the configured separator and outputs a list of the substrings",
    icon="fa-cut",
    label="split string, divide text, break string, tokenize text, parse string",
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
    description="Slices a list or string using the configured start and end indexes.",
    icon="fa-cut",
    label="slice list, extract portion, get segment, subset sequence, partial list",
)
class Slice(Block):
    start: Annotated[int, Config()] = 0
    end: Annotated[int, Config()] = 0

    @step(output_name="items")
    async def slice(self, items: list[Any] | str) -> list[Any] | str:
        return items[self.start : self.end]


@metadata(
    category=BlockCategory.FUNCTION,
    description="Gets the first item from a list",
    icon="fa-arrow-alt-circle-left",
)
class First(OperatorBlock, Generic[firstItemT]):
    @step(output_name="item")
    async def first(self, items: list[firstItemT]) -> firstItemT:
        return items[0]


@metadata(
    category=BlockCategory.FUNCTION,
    description="Flattens a list of lists into a single list",
    icon="fa-compress",
    label="flatten list, merge nested lists, combine nested arrays, unnest lists, simplify nested lists",
)
class Flatten(OperatorBlock):
    @step(output_name="list")
    async def flatten(self, lists: list[list[Any]]) -> list[Any]:
        return list(flatten(lists))


@metadata(
    description="Takes in inputs and creates a list containing the inputs.",
    category=BlockCategory.MISC,
    icon="fa-list-ul",
    label="create list, build list, construct list, form list, make list",
)
class CreateList(Block):
    @step(output_name="list")
    async def build(self, *items: Any) -> list[Any]:
        return list(items)


@metadata(
    category=BlockCategory.FUNCTION,
    description="Appends an item to a list and outputs the updated list. Maintains the list state across calls.",
    label="list builder, dynamic list, item aggregation, list accumulation, append to list",
)
class BuildList(Block):
    items: Annotated[list[Any], State()] = []

    @step(output_name="items")
    async def create_response(self, item: Any) -> list[Any]:
        self.items.append(item)
        return self.items


@metadata(
    category=BlockCategory.FUNCTION,
    description="Merges objects from two lists by matching on the configured key.",
    obsolete=True,
    label="merge JSON lists, combine JSON arrays, join JSON objects, match and merge, consolidate JSON data",
    use_instead="Join",
)
class MergeLists(Block):
    key: Annotated[str, Config()]

    @step(output_name="result")
    async def merge_lists(
        self,
        a: list[dict[str, Any]],
        b: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        dict1 = {item[self.key]: item for item in a}
        dict2 = {item[self.key]: item for item in b}

        merged_dict = {}
        for code in dict1.keys() | dict2.keys():
            if code in dict1 and code in dict2:
                merged_dict[code] = {**dict1[code], **dict2[code]}
            elif code in dict1:
                merged_dict[code] = dict1[code]
            elif code in dict2:
                merged_dict[code] = dict2[code]

        final_result = list(merged_dict.values())

        return final_result


@metadata(
    description="Takes in a list and sends each item to the corresponding output",
    category=BlockCategory.MISC,
    icon="fa-th-list",
    label="unpack list, distribute items, extract list elements, spread array, decompose list",
)
class UnpackList(Block):
    items: list[Output[Any]]

    @step()
    async def unpack(self, list: list[Any]):
        for i, v in enumerate(list):
            if len(self.items) > i:
                self.items[i].send(v)


@metadata(
    description="Appends item to items and output resulting list",
    category=BlockCategory.MISC,
    icon="fa-plus",
    label="append item, add item, extend list, insert item, concatenate item",
)
class Append(Block, Generic[ItemT]):
    @step(output_name="items")
    async def build(self, items: list[ItemT], item: ItemT) -> list[ItemT]:
        items.append(item)
        return items
