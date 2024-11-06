{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `IntegerConst` Block takes a predefined integer as configuration and outputs it. This Block is useful for setting up constant integer values that can be referenced across workflows when a static numerical input is needed.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Output a predefined integer
- Create an `IntegerConst` Block.
- Set the `output` configuration to `42`.
- The Block will output the integer `42`.

### Example 2: Use as a constant value in a calculation
- Set up an `IntegerConst` Block with `output` set to `10`.
- Use this Block's output in downstream Blocks for calculations or as a constant reference.

## Error Handling
- If the `output` configuration is not set to an integer, the Block will raise a `TypeError`.
- This Block assumes a valid integer is provided in the configuration.

## FAQ

???+ question "Can the integer value change during execution?"

    No, the `IntegerConst` Block outputs a static integer based on its configuration. It is intended for constant values that do not vary during the workflow.

???+ question "What happens if `output` is not configured?"

    If `output` is not set, the Block will raise a configuration error. The `output` configuration is required and must be an integer.

???+ question "Can I use negative integers?"

    Yes, you can set `output` to any integer value, including negative integers, and the Block will output it as configured.
