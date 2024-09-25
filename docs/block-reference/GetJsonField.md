{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `GetJsonField` Block uses JSONPath to extract specific data from a JSON object or list. JSONPath is a query language used to traverse and extract data from JSON structures. This Block is marked as obsolete, meaning it may no longer be recommended for use in future workflows.

It accepts JSON input, which can be a JSON object or a list of JSON objects, and applies a JSONPath expression to extract the specified fields.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Extract a field from a JSON object
- Create a `GetJsonField` Block.
- Set the `json_field_structure` to `$.name` (this JSONPath expression extracts the "name" field).
- Provide the input JSON object: `{"name": "John", "age": 30}`.
- The Block will output `["John"]`, extracting the "name" field.

### Example 2: Extract multiple fields from a list of JSON objects
- Set up a `GetJsonField` Block.
- Set the `json_field_structure` to `$[*].name` (this JSONPath expression extracts the "name" field from all objects in the list).
- Provide the input JSON list: `[{"name": "John"}, {"name": "Jane"}]`.
- The Block will output `["John", "Jane"]`.

### Example 3: Handle nested fields in a complex JSON structure
- Create a `GetJsonField` Block.
- Set the `json_field_structure` to `$.address.city`.
- Provide the input: `{"address": {"city": "Auckland", "postcode": "1010"}}`.
- The Block will output `["Auckland"]`, extracting the "city" field from the nested "address" object.

## Error Handling
- If the `json_field_structure` is not a valid JSONPath expression, the Block will raise an error.
- If the JSON object or list does not contain the field specified by the JSONPath, the Block will return an empty list.
- If the input JSON is malformed or not valid, an error will be raised.

## FAQ

???+ question "What happens if the JSONPath expression doesn't match any field?"
    
    If the JSONPath expression doesn't match any field in the input JSON, the Block will return an empty list. Ensure the JSONPath expression is correct for the structure of the input JSON.

???+ question "Can this Block handle both JSON objects and lists?"
    
    Yes, the `GetJsonField` Block works with both individual JSON objects and lists of JSON objects. It will apply the JSONPath expression to extract the relevant fields from either structure.

???+ question "What does it mean that this Block is obsolete?"
    
    The `GetJsonField` Block has been marked as obsolete, meaning it may no longer be recommended for use in new workflows and could be removed in future updates. It's advisable to explore alternative methods for extracting JSON fields.

???+ question "How does the Block handle complex nested JSON structures?"
    
    The `GetJsonField` Block can handle complex nested JSON structures by using appropriate JSONPath expressions. For example, you can extract deeply nested fields by specifying the correct path in the `json_field_structure`.