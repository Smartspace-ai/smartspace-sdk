{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `Cast` Block converts an input into the specified type based on a provided schema. This is useful for ensuring that inputs conform to a specific structure or type.

{{ generate_block_details_smartspace(page.title) }}

## Example(s)

### Example 1: Cast a string to a number
- Create a `Cast` Block.
- Set the schema to `{"type": "number"}`.
- Provide the input: `"123"`.
- The Block will output: `123`.

### Example 2: Cast a JSON string to an object
- Set up a `Cast` Block.
- Set the schema to `{"type": "object"}`.
- Provide the input: `'{"name": "John"}'`.
- The Block will output: `{"name": "John"}`.

## Error Handling
- If the input cannot be cast to the specified type, the Block will raise a `ValueError`.

## FAQ

???+ question "What happens if the input doesn't match the schema?"

    The Block will raise an error or attempt to convert the input according to the schema.

