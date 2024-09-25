{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `MergeLists` Block merges two lists of objects (dictionaries) based on a matching key. It takes two input lists and combines the dictionaries from both lists where the specified key is equal. If both lists contain objects with the same key, their values are merged, with values from the second list overriding those from the first in case of conflicts.

This Block is useful for combining datasets or lists where you need to merge records with the same identifier.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Merge two lists of dictionaries
- Create a `MergeLists` Block.
- Set the `key` to `"id"`.
- Provide the input lists:
  - `a = [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]`
  - `b = [{"id": 1, "age": 30}, {"id": 3, "name": "Jim"}]`
- The Block will output:
  ```json
  [
    {"id": 1, "name": "John", "age": 30},
    {"id": 2, "name": "Jane"},
    {"id": 3, "name": "Jim"}
  ]
  ```

### Example 2: Handle missing keys in one list
- Set up a `MergeLists` Block.
- Set the `key` to `"code"`.
- Provide the input lists:
  - `a = [{"code": "A", "value": 100}, {"code": "B", "value": 200}]`
  - `b = [{"code": "A", "description": "First"}, {"code": "C", "value": 300}]`
- The Block will output:
  ```json
  [
    {"code": "A", "value": 100, "description": "First"},
    {"code": "B", "value": 200},
    {"code": "C", "value": 300}
  ]
  ```

### Example 3: Merge lists with no overlapping keys
- Create a `MergeLists` Block.
- Set the `key` to `"id"`.
- Provide two lists with no overlapping keys:
  - `a = [{"id": 1, "data": "X"}]`
  - `b = [{"id": 2, "data": "Y"}]`
- The Block will output:
  ```json
  [
    {"id": 1, "data": "X"},
    {"id": 2, "data": "Y"}
  ]
  ```

## Error Handling
- If any object in the input lists does not contain the specified key, the Block will raise a `KeyError`. Ensure that all objects in both lists contain the key specified in the `key` configuration.
- The Block assumes that the values of the key field are unique within each list. If there are duplicate keys within a list, the Block will only consider the last occurrence of each key.

## FAQ

???+ question "What happens if one list has objects with keys that don't exist in the other list?"
    
    The Block will still include those objects in the final result. Objects that only exist in one list will be added as-is without merging.

???+ question "What if the two lists have different fields for the same key?"
    
    If both lists contain objects with the same key but different fields, the resulting merged object will include fields from both lists. In case of conflicting fields, the values from the second list will override the values from the first list.

???+ question "Can I merge more than two lists using this Block?"
    
    The `MergeLists` Block only supports merging two lists at a time. To merge more than two lists, you can chain multiple `MergeLists` Blocks or merge the lists step by step.

???+ question "What if a list contains duplicate keys?"
    
    If either list contains duplicate keys, only the last occurrence of each key will be considered. The Block does not handle merging objects with duplicate keys within a single list.