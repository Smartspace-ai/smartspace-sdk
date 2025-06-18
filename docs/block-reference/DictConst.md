{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `DictConst` Block outputs a predefined dictionary (object) that is configured when the Block is set up. This Block is useful for providing static data structures, configuration objects, or default values in your workflows. The dictionary is specified in the Block's configuration and remains constant throughout execution.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Output a simple configuration object
- Create a `DictConst` Block.
- Configure the output dictionary: `{"host": "localhost", "port": 8080, "debug": true}`.
- The Block will output: `{"host": "localhost", "port": 8080, "debug": true}`.

### Example 2: Provide user profile data
- Set up a `DictConst` Block.
- Configure the dictionary: `{"name": "John Doe", "role": "admin", "permissions": ["read", "write", "delete"]}`.
- The Block will output the configured user profile object.

### Example 3: Supply API endpoint configuration
- Create a `DictConst` Block.
- Configure with: `{"baseUrl": "https://api.example.com", "version": "v2", "timeout": 30}`.
- The Block will consistently output this API configuration object.

### Example 4: Handle empty dictionary
- Set up a `DictConst` Block.
- Configure with an empty dictionary: `{}`.
- The Block will output an empty object `{}`.

## Error Handling
- The `DictConst` Block has minimal error handling requirements since it outputs a pre-configured static value.
- If the configured dictionary contains invalid JSON syntax during setup, the Block configuration will fail.
- The Block will always output the exact dictionary structure that was configured, maintaining data type consistency.

## FAQ

???+ question "Can I modify the dictionary after the Block is configured?"

    No, the `DictConst` Block outputs a constant dictionary that is set during configuration. If you need to modify dictionary values dynamically, consider using other blocks like `TemplatedObject` or `CreateObject`.

???+ question "What types of values can I include in the dictionary?"

    The dictionary can contain any valid JSON data types including strings, numbers, booleans, arrays, and nested objects. Complex data structures are fully supported.

???+ question "Can I use this Block to provide default values for other Blocks?"

    Yes, `DictConst` is excellent for providing default configuration objects or fallback values that other Blocks can use when specific inputs are not available.

???+ question "How does this differ from other constant Blocks?"

    `DictConst` specifically outputs dictionary/object structures, while `StringConst` outputs strings and `IntegerConst` outputs numbers. Use `DictConst` when you need to provide structured data or configuration objects.

???+ question "Can the output dictionary contain nested objects and arrays?"

    Yes, the `DictConst` Block supports arbitrarily complex nested dictionary structures, including nested objects, arrays, and mixed data types, as long as the structure is valid JSON.

