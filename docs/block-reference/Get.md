{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `Get` Block extracts data from a JSON object or list using a JSONPath expression. JSONPath is a query language for navigating and extracting elements from JSON structures. This implementation uses the `jsonpath-ng` library from [PyPI](https://pypi.org/project/jsonpath-ng/).

You can configure the JSONPath expression via the `path` parameter, and the Block will return the extracted data based on that path.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Extract a field from a JSON object
- Create a `Get` Block.
- Set the `path` to `$.name` (this JSONPath expression extracts the "name" field).
- Provide the input JSON object: `{"name": "John", "age": 30}`.
- The Block will output `"John"`, extracting the "name" field.

### Example 2: Extract multiple fields from a list of JSON objects
- Set up a `Get` Block.
- Set the `path` to `$[*].name` (this JSONPath expression extracts the "name" field from all objects in the list).
- Provide the input JSON list: `[{"name": "John"}, {"name": "Jane"}]`.
- The Block will output `["John", "Jane"]`.

### Example 3: Handle nested fields in a complex JSON structure
- Create a `Get` Block.
- Set the `path` to `$.address.city`.
- Provide the input: `{"address": {"city": "Auckland", "postcode": "1010"}}`.
- The Block will output `"Auckland"`, extracting the "city" field from the nested "address" object.

## Error Handling
- If the `path` is not a valid JSONPath expression, the Block will raise an error.
- If no match is found for the JSONPath, the Block will return `None` for individual JSON objects or an empty list for lists.
- Ensure the input JSON is well-formed; otherwise, the Block may raise an error.

## FAQ

???+ question "What happens if the JSONPath expression doesn't match any field?"
    
    If the JSONPath expression does not match any field in the input, the Block will return `None` for a single JSON object and an empty list for a list of JSON objects.

???+ question "Can I use this Block for both JSON objects and lists?"
    
    Yes, the `Get` Block supports both JSON objects and lists. For lists, it will return all matching fields as a list of values. For single JSON objects, it will return the first match or `None` if no match is found.

???+ question "How does the Block handle nested fields?"
    
    The `Get` Block uses JSONPath expressions to navigate and extract fields from nested JSON structures. By specifying the correct path, you can extract deeply nested fields from JSON objects.

???+ question "What happens if multiple matches are found?"
    
    For lists, the `Get` Block will return all matching elements. For a single JSON object, the Block returns only the first match found. If you need all matches from an object, you should ensure the input is structured as a list.