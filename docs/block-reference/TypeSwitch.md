{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `TypeSwitch` Block allows you to select different outputs based on the schema of the input. This is useful when you need to handle multiple types of inputs and route them to different outputs based on their type.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Switch based on input type
- Create a `TypeSwitch` Block.
- Define two options: one for strings and one for numbers.
- Provide the input `"Hello"` (string).
- The Block will send `"Hello"` to the string output.

## Error Handling
- If the input does not match any defined schema, the Block will not send the input to any output.

## FAQ

???+ question "What happens if the input does not match any schema?"

    The Block will skip the input, and no outputs will be triggered.