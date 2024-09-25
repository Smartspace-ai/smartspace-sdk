{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `ParseJson` Block parses a JSON string or a list of JSON strings into Python dictionaries. This Block accepts either a single JSON string or a list of JSON strings and converts them into their corresponding dictionary or list of dictionaries, respectively. It is useful when you need to work with structured JSON data in subsequent steps.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Parse a single JSON string
- Create a `ParseJson` Block.
- Provide the input: `'{"name": "John", "age": 30}'`.
- The Block will parse the JSON string and output: `{"name": "John", "age": 30}` as a dictionary.

### Example 2: Parse a list of JSON strings
- Set up a `ParseJson` Block.
- Provide a list of JSON strings: `['{"name": "John"}', '{"name": "Jane"}']`.
- The Block will output: `[{"name": "John"}, {"name": "Jane"}]`, a list of dictionaries.

### Example 3: Handle invalid JSON
- Create a `ParseJson` Block.
- Provide an invalid JSON string: `'{"name": "John"'`.
- The Block will raise a `JSONDecodeError` due to the invalid JSON format.

## Error Handling
- If the input is not a valid JSON string, the Block will raise a `JSONDecodeError`.
- If a list of JSON strings is provided and any of them are invalid, the Block will raise an error indicating which string caused the issue.
- If the input is neither a string nor a list of strings, the Block will raise an error.

## FAQ

???+ question "What happens if I provide an invalid JSON string?"
    
    If you provide an invalid JSON string, the `ParseJson` Block will raise a `JSONDecodeError`. Make sure that the JSON string is well-formed and valid before passing it to the Block.

???+ question "Can I pass both single and multiple JSON strings?"
    
    Yes, the `ParseJson` Block accepts both a single JSON string and a list of JSON strings. It will parse each string individually and return the appropriate Python dictionary or list of dictionaries.

???+ question "What happens if I pass an empty string?"
    
    If an empty string is provided, the `ParseJson` Block will raise a `JSONDecodeError`, as an empty string is not valid JSON.

???+ question "Does this Block handle complex JSON structures?"
    
    Yes, the `ParseJson` Block can handle complex JSON structures, including nested objects and arrays. It will parse them into corresponding Python dictionaries and lists.