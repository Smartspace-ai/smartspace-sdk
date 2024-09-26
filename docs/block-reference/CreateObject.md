{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `CreateObject` Block constructs an object (dictionary) from the given key-value pairs. This is useful when you need to dynamically build an object with properties.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Create an object from properties
- Create a `CreateObject` Block.
- Provide inputs: `{"name": "John", "age": 30}`.
- The Block will output: `{"name": "John", "age": 30}`.

## Error Handling
- The Block assumes that all provided inputs are valid key-value pairs.

## FAQ

???+ question "Can I create an object with nested properties?"

    Yes, you can include nested objects within the properties.