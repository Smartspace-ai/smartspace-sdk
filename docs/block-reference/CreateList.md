{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `CreateList` Block creates a list from the provided items. This is useful when you need to build a list dynamically from multiple inputs.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Create a list from items
- Create a `CreateList` Block.
- Provide inputs: `1, 2, 3`.
- The Block will output: `[1, 2, 3]`.

## Error Handling
- The Block will raise an error if the inputs cannot be converted to a list.

## FAQ

???+ question "What happens if no items are provided?"

    The Block will return an empty list if no items are provided.