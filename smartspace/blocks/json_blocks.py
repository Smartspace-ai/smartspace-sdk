import json
import re
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
    Output,
    State,
    metadata,
    step,
)
from smartspace.enums import BlockCategory


@metadata(
    description="This block takes a JSON string or a list of JSON strings and parses them",
    category=BlockCategory.FUNCTION,
    icon="fa-code",
    label="parse JSON, convert JSON string, decode JSON, JSON deserialize, extract JSON data",
)
class ParseJson(OperatorBlock):
    @step(output_name="json")
    async def parse_json(
        self,
        json_string: Annotated[
            Union[str, List[str]],
            Metadata(description="JSON string or list of JSON strings"),
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
    description="This block removes a specified key from a JSON object. If 'recursive' is set to true, it recursively removes the key from all nested dictionaries; otherwise, it only removes the key from the top level. Returns a copy of the object with the key removed.",
    category=BlockCategory.FUNCTION,
    icon="fa-code",
    label="Remove Key from any json object",
)
class RemoveProperty(OperatorBlock):
    key: Annotated[str, Config()]
    recursive: Annotated[bool, Config()] = False

    @step(output_name="json")
    async def process_object(
        self,
        object: Annotated[
            dict, Metadata(description="Input JSON object as a dictionary")
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
    description="This block retrieves the keys of a JSON object (dictionary). Returns a list of keys.",
    category=BlockCategory.FUNCTION,
    icon="fa-code",
    label="Get Keys from json object",
)
class GetKeys(OperatorBlock):
    @step(output_name="keys")
    async def process_json(
        self,
        object: Annotated[
            dict, Metadata(description="Input JSON object as a dictionary")
        ],
    ) -> List[str]:
        return list(object.keys())


@metadata(
    category=BlockCategory.FUNCTION,
    description="Uses JSONPath to extract data from a JSON object or list. This block will be moved to connection configuration in a future version",
    obsolete=True,
    label="extract JSON field, get JSON value, access JSON data, retrieve JSON property, JSON path query",
    use_instead="Get",
)
class GetJsonField(Block):
    json_field_structure: Annotated[str, Config()]

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
    description="Uses JSONPath to extract data from a JSON object or list.\nJSONPath implementation is from https://pypi.org/project/jsonpath-ng/.",
    icon="fa-search",
    label="get JSON path, query JSON data, extract JSON values, JSON lookup, search JSON",
)
class Get(OperatorBlock):
    path: Annotated[str, Config()]

    @step(output_name="result")
    async def get(self, data: list[Any] | dict[str, Any]) -> Any:
        jsonpath_expr: JSONPath = parse(self.path)
        if isinstance(data, list):
            return [match.value for match in jsonpath_expr.find(data)]
        else:
            results = [match.value for match in jsonpath_expr.find(data)]
            return None if not len(results) else results[0]


class JoinType(Enum):
    INNER = "inner"
    OUTER = "outer"
    LEFT_INNER = "left_inner"
    LEFT_OUTER = "left_outer"
    RIGHT_INNER = "right_inner"
    RIGHT_OUTER = "right_outer"


@metadata(
    category=BlockCategory.FUNCTION,
    description="""
The `Join` block performs advanced join operations between two lists of dictionaries based on a specified key. It merges the data according to the selected join type, similar to SQL join operations, allowing for flexible data integration and transformation.

**Key Features**:

- **Flexible Join Types**: Supports multiple join types, including `INNER`, `LEFT_INNER`, `LEFT_OUTER`, `RIGHT_INNER`, `RIGHT_OUTER`, and `OUTER`.
- **Customizable Key**: Allows specification of the join key.
- **Data Merging**: Combines fields from both left and right records where applicable.
- **Error Handling**: Ensures all records contain the specified key.

**Supported Join Types**:

- **INNER**: Records where the key exists in both left and right lists.
- **LEFT_INNER**: Left records with matching keys in the right list.
- **LEFT_OUTER**: All left records, merging with right records where keys match.
- **RIGHT_INNER**: Right records with matching keys in the left list.
- **RIGHT_OUTER**: All right records, merging with left records where keys match.
- **OUTER**: All records from both lists, merging where keys match.

**Use Cases**:

- Merging datasets from different sources.
- Performing SQL-like join operations in Python.
""",
    icon="fa-link",
    label="join JSON data, SQL-like join, merge datasets, combine JSON lists, data integration",
)
class Join(Block):
    key: Annotated[str, Config()]
    joinType: Annotated[JoinType, Config()] = JoinType.INNER

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


@metadata(
    description="Merges multiple dictionaries into a single object. Accepts only dicts and combines all key-value pairs into one dictionary.",
    category=BlockCategory.MISC,
    icon="fa-cube",
    label="merge objects, combine dictionaries, build object, aggregate key-value pairs",
)
class MergeObjects(Block):
    @step(output_name="object")
    async def build(self, *objects: dict[str, Any]) -> dict[str, Any]:
        merged_object = {}
        for obj in objects:
            merged_object.update(obj)
        return merged_object


@metadata(
    description="Takes in inputs and creates an object containing the inputs",
    category=BlockCategory.MISC,
    icon="fa-cube",
    label="create object, build dictionary, construct object, make key-value map, generate object",
)
class CreateObject(Block):
    @step(output_name="object")
    async def build(self, **properties: Any) -> dict[str, Any]:
        return properties


@metadata(
    category=BlockCategory.FUNCTION,
    label="object builder, json merge, dictionary update, data aggregation, object construction",
    description="Merges objects using dictionary unpacking (similar to jq's merge). Each new object is merged with the existing accumulated object.",
)
class BuildObject(Block):
    """
    A block that merges objects using dictionary unpacking (similar to jq's merge).
    Each new object is merged with the existing accumulated object.
    """

    merged_object: Annotated[dict[str, Any], State()] = {}

    @step(output_name="merged_object")
    async def merge_object(self, obj: dict[str, Any]) -> dict[str, Any]:
        # If a string is passed, try to parse it as JSON
        if isinstance(obj, str):
            cleaned_str = obj.strip()

            # Remove markdown code block syntax if present
            markdown_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
            markdown_match = re.search(markdown_pattern, cleaned_str)
            if markdown_match:
                cleaned_str = markdown_match.group(1).strip()

            # Remove potential control characters
            cleaned_str = re.sub(r"[\x00-\x1F\x7F]", "", cleaned_str)

            # Ensure proper JSON formatting for common issues
            if not cleaned_str.startswith("{") and not cleaned_str.startswith("["):
                # Try to find the first occurrence of '{' or '['
                json_start = min(
                    (
                        cleaned_str.find("{")
                        if cleaned_str.find("{") >= 0
                        else float("inf")
                    ),
                    (
                        cleaned_str.find("[")
                        if cleaned_str.find("[") >= 0
                        else float("inf")
                    ),
                )
                if json_start != float("inf"):
                    cleaned_str = cleaned_str[json_start:]

            obj = json.loads(cleaned_str)

        self.merged_object = {**self.merged_object, **obj}
        return self.merged_object


@metadata(
    description="Takes in an object and sends each key-value pair to the corresponding output",
    category=BlockCategory.MISC,
    icon="fa-th-large",
    label="unpack object, extract object properties, decompose dictionary, spread object, distribute fields",
)
class UnpackObject(Block):
    properties: dict[str, Output[dict[str, Any]]]

    @step()
    async def unpack(self, object: dict[str, Any]):
        for name, value in object.items():
            if name in self.properties:
                self.properties[name].send(value)
