{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `UnpackObject` Block extracts the properties of an object and sends them to the corresponding outputs. This is useful when you need to access individual properties of an object.

{{ generate_block_details_smartspace(page.title) }}

## Example(s)

### Example 1: Unpack an object into properties
- Create an `UnpackObject` Block.
- Set the `properties` to output `name` and `age`.
- Provide the input object: `{"name": "John", "age": 30}`.
- The Block will send `"John"` to the `name` output and `30` to the `age` output.

## Error Handling
- If a property in the object is not mapped to an output, it will be ignored.

## FAQ

???+ question "What happens if the object contains properties not defined in `properties`?"

    Those properties will be ignored unless explicitly defined in the Block’s `properties`.

