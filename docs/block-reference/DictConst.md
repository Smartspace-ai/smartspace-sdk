{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}


## Overview
The `DictConst` Block takes a predefined dictionary as configuration and outputs it. This Block is useful for setting up constant values or configuration data that can be used in workflows where a static dictionary is needed as an input.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Output a predefined dictionary
- Create a `DictConst` Block.
- Set the `output` configuration to `{"key1": "value1", "key2": "value2"}`.
- The Block will output the configured dictionary as it is defined.

### Example 2: Use in a workflow for static configuration data
- Set up a `DictConst` Block with a dictionary for configuration.
- Use the output in downstream blocks to provide consistent configuration values across the workflow.

## Error Handling
- If the `output` configuration is not set to a dictionary, the Block will raise a `TypeError`.
- This Block expects a valid dictionary in the configuration and will not modify the data.

## FAQ

???+ question "Can I change the dictionary dynamically?"

    No, the `DictConst` Block outputs a static dictionary based on its configuration. It is intended for constant values that do not change during workflow execution.

???+ question "What happens if the `output` configuration is empty?"

    If the `output` configuration is an empty dictionary `{}`, the Block will simply output an empty dictionary as configured.

???+ question "Can I use complex dictionaries with nested structures?"

    Yes, you can define complex dictionaries with nested structures in the `output` configuration. The Block will output the dictionary exactly as it is configured.
