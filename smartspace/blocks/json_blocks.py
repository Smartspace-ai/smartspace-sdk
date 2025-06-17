import json
from enum import Enum
from typing import Annotated, Any, List, Union

from jsonpath_ng import JSONPath
from jsonpath_ng.ext import parse
from pydantic import BaseModel

from smartspace.core import (
    Block,
    Config,
    Metadata,
    OperatorBlock,
    metadata,
    step,
)
from smartspace.enums import BlockCategory


@metadata(
    description="This block takes a JSON string or a list of JSON strings and parses them",
    category=BlockCategory.FUNCTION,
    icon="fa-code",
    label="parse JSON, convert JSON string, decode JSON, JSON deserialize, extract JSON data",
    obsolete=True,
    deprecated_reason="This block will be deprecated and moved to connection configuration in a future version.",
)
class ParseJson(OperatorBlock):
    @step(output_name="json")
    async def parse_json(
        self,
        json_string: Annotated[
            Union[str, List[str]],
            Metadata(description="JSON text to parse or list of JSON strings."),
        ],
    ) -> dict[str, Any] | list[dict[str, Any]]:
        if isinstance(json_string, dict):
            return json_string
        elif isinstance(json_string, list):
            results: list[Any] = [json.loads(item) for item in json_string]
            return results
        else:
            result = json.loads(json_string)
            return result


@metadata(
    description="Removes a specified property from JSON objects. Optionally removes the property recursively from nested objects. Use this to clean or filter object data.",
    category=BlockCategory.FUNCTION,
    icon="fa-code",
    label="remove property, delete key, filter object, clean data, modify json",
)
class RemoveProperty(OperatorBlock):
    key: Annotated[str, Config(), Metadata(description="Property name to remove from the object.")]
    recursive: Annotated[bool, Config(), Metadata(description="Remove property from nested objects recursively.")]

    @step(output_name="json")
    async def process_object(
        self,
        object: Annotated[
            dict, Metadata(description="JSON object to remove property from.")
        ],
    ) -> dict:
        if self.recursive:

            def recursive_remove(item: dict):
                if self.key in item:
                    item.pop(self.key)
                for key, value in list(item.items()):
                    if isinstance(value, dict):
                        recursive_remove(value)

            recursive_remove(object)
        else:
            if self.key in object:
                object.pop(self.key)
        return object


@metadata(
    description="Extracts all property names from a JSON object. Returns a list of keys for inspection or iteration. Use this to analyze object structure.",
    category=BlockCategory.FUNCTION,
    icon="fa-code",
    label="get keys, object properties, extract keys, list fields, inspect structure",
)
class GetKeys(OperatorBlock):
    @step(output_name="keys")
    async def process_json(
        self,
        object: Annotated[
            dict, Metadata(description="JSON object to extract keys from.")
        ],
    ) -> List[str]:
        return list(object.keys())


@metadata(
    category=BlockCategory.FUNCTION,
    description="Uses JSONPath to extract data from a JSON object or list. This block will be moved to connection configuration in a future version",
    obsolete=True,
    label="extract JSON field, get JSON value, access JSON data, retrieve JSON property, JSON path query",
    deprecated_reason="This block will be deprecated and moved to connection configuration in a future version.",
)
class GetJsonField(Block):
    json_field_structure: Annotated[str, Config(), Metadata(description="JSONPath expression for data extraction.")]

    @step(output_name="field")
    async def get(self, json_object: Any) -> Any:
        if isinstance(json_object, BaseModel):
            json_object = json.loads(json_object.model_dump_json())
        elif isinstance(json_object, list) and all(
            isinstance(item, BaseModel) for item in json_object
        ):
            json_object = [json.loads(item.model_dump_json()) for item in json_object]

        jsonpath_expr: JSONPath = parse(self.json_field_structure)
        results: List[Any] = [match.value for match in jsonpath_expr.find(json_object)]
        return results


@metadata(
    category=BlockCategory.FUNCTION,
    description="Extracts data from JSON using JSONPath queries. Supports complex nested data retrieval with path expressions. Use this for precise data extraction.",
    icon="fa-search",
    label="json path, extract data, query json, data lookup, search nested",
)
class Get(OperatorBlock):
    path: Annotated[str, Config(), Metadata(description="JSONPath expression to query data.")]

    @step(output_name="result")
    async def get(self, data: list[Any] | dict[str, Any]) -> Any:
        jsonpath_expr: JSONPath = parse(self.path)
        if isinstance(data, list):
            return [match.value for match in jsonpath_expr.find(data)]
        else:
            results = [match.value for match in jsonpath_expr.find(data)]
            return None if not len(results) else results[0]


@metadata(
    category=BlockCategory.FUNCTION,
    description="Merges objects from two lists by matching on the configured key.",
    obsolete=True,
    label="merge JSON lists, combine JSON arrays, join JSON objects, match and merge, consolidate JSON data",
    use_instead="Concat",
    deprecated_reason="This block will be deprecated in a future version. Use Concat instead.",
)
class MergeLists(Block):
    key: Annotated[str, Config(), Metadata(description="Property name to match objects on.")]

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


class JoinType(Enum):
    INNER = "inner"
    OUTER = "outer"
    LEFT_INNER = "left_inner"
    LEFT_OUTER = "left_outer"
    RIGHT_INNER = "right_inner"
    RIGHT_OUTER = "right_outer"


@metadata(
    category=BlockCategory.FUNCTION,
    description="Merges two lists of objects using SQL-style join operations. Combines records based on matching key values with configurable join types. Use this to integrate data from multiple sources.",
    icon="fa-link",
    label="join data, merge lists, sql join, combine objects, data integration",
)
class Join(Block):
    key: Annotated[str, Config(), Metadata(description="Property name to join objects on.")]
    joinType: Annotated[JoinType, Config(), Metadata(description="Type of join operation to perform.")]

    @step(output_name="result")
    async def Join(
        self,
        left: list[dict[str, Any]],
        right: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        # Create dictionaries mapping key values to records
        left_dict = {}
        for item in left:
            key_value = item.get(self.key)
            if key_value is None:
                raise KeyError(
                    f"Left item {item} does not contain the key '{self.key}'"
                )
            left_dict[key_value] = item

        right_dict = {}
        for item in right:
            key_value = item.get(self.key)
            if key_value is None:
                raise KeyError(
                    f"Right item {item} does not contain the key '{self.key}'"
                )
            right_dict[key_value] = item

        # Determine the keys to include based on the join type
        if self.joinType == JoinType.INNER:
            keys = set(left_dict.keys()) & set(right_dict.keys())
        elif self.joinType == JoinType.LEFT_INNER:
            keys = set(k for k in left_dict.keys() if k in right_dict)
        elif self.joinType == JoinType.LEFT_OUTER:
            keys = set(left_dict.keys())
        elif self.joinType == JoinType.RIGHT_INNER:
            keys = set(k for k in right_dict.keys() if k in left_dict)
        elif self.joinType == JoinType.RIGHT_OUTER:
            keys = set(right_dict.keys())
        elif self.joinType == JoinType.OUTER:
            keys = set(left_dict.keys()) | set(right_dict.keys())
        else:
            raise ValueError(
                f"Invalid joinType '{self.joinType}'. Must be one of JoinType."
            )

        # Merge the records based on the keys
        result = []
        for key in keys:
            merged_item = {}
            left_item = left_dict.get(key)
            right_item = right_dict.get(key)

            if self.joinType in (
                JoinType.LEFT_OUTER,
                JoinType.LEFT_INNER,
                JoinType.INNER,
                JoinType.OUTER,
            ):
                if left_item:
                    merged_item.update(left_item)
            if self.joinType in (
                JoinType.RIGHT_OUTER,
                JoinType.RIGHT_INNER,
                JoinType.INNER,
                JoinType.OUTER,
            ):
                if right_item:
                    merged_item.update(right_item)

            # Only include items that have data
            if merged_item:
                result.append(merged_item)

        return result
