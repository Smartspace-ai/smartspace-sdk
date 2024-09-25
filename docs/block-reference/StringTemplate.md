{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `StringTemplate` Block allows you to generate a string by using a template and dynamically inserting values into it. This is useful when you want to build strings based on inputs with specific formatting. It uses the [jinja2](https://jinja.palletsprojects.com/en/3.1.x/) templating engine to render the template.

{{ generate_block_details_smartspace(page.title) }}

## Example(s)

### Example 1: Build a string with dynamic values
- Create a `StringTemplate` Block.
- Set the `template` to `"Hello, {{name}}!"`.
- Provide the input: `{"name": "John"}`.
- The Block will output: `"Hello, John!"`.

## Error Handling
- If the template contains invalid syntax, the Block will raise an error.

## FAQ

???+ question "What happens if a required input is missing?"

    The Block will raise a `KeyError` if the template expects a variable that is not provided in the inputs.