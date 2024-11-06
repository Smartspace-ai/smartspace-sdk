{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `StringConst` Block takes a predefined string as configuration and outputs it. This Block is useful for setting up constant string values that can be referenced across workflows when a static text input is needed.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Output a predefined string
- Create a `StringConst` Block.
- Set the `output` configuration to `"Hello, World!"`.
- The Block will output the string `"Hello, World!"`.

### Example 2: Use as a constant text in a workflow
- Set up a `StringConst` Block with `output` set to `"Config Value"`.
- Use this Block's output in downstream Blocks to provide a consistent string reference.

## Error Handling
- If the `output` configuration is not set to a string, the Block will raise a `TypeError`.
- This Block expects a valid string to be provided in the configuration.

## FAQ

???+ question "Can the string value change during execution?"

    No, the `StringConst` Block outputs a static string based on its configuration. It is intended for constant values that do not vary during the workflow.

???+ question "What happens if `output` is not configured?"

    If `output` is not set, the Block will raise a configuration error. The `output` configuration is required and must be a string.

???+ question "Can I use special characters in the string?"

    Yes, you can use any characters in the string, including special characters, and the Block will output it as configured.