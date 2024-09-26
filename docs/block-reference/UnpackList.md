{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `UnpackList` Block extracts elements from a list and sends them to the corresponding outputs. This is useful when you need to access individual elements of a list.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Unpack a list into individual items
- Create an `UnpackList` Block.
- Set the `items` to output the first three elements of the list.
- Provide the input list: `[1, 2, 3, 4]`.
- The Block will send `1`, `2`, and `3` to the first three outputs.

## Error Handling
- If the list contains more elements than the defined outputs, the extra elements will be ignored.

## FAQ

???+ question "What happens if the list has fewer elements than the outputs?"

    The outputs for the missing elements will not receive any values.

