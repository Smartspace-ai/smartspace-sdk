{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `SplitString` Block is used to split a string into a list of substrings based on a configured separator. The separator can be customized, and an option is available to include the separator as part of the resulting substrings. By default, the separator is set to a newline character (`\n`).

This Block is useful for cases where you need to break a string into smaller parts, such as splitting a text file into lines or splitting a sentence into words.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Split a string by newline
- Create a `SplitString` Block.
- Use the default separator (`"\n"`).
- Provide the input string: `"apple\nbanana\ncherry"`.
- The output will be `["apple", "banana", "cherry"]`.

### Example 2: Split a string by a comma
- Create a `SplitString` Block.
- Set the `separator` to `","`.
- Provide the input string: `"apple,banana,cherry"`.
- The output will be `["apple", "banana", "cherry"]`.

### Example 3: Include the separator in the result
- Set up a `SplitString` Block.
- Set the `separator` to `" "`, and enable `include_separator`.
- Provide the input string: `"apple banana cherry"`.
- The output will be `["apple ", "banana ", "cherry"]`.

## Error Handling
- The `SplitString` Block expects a valid string as input. If a non-string value is passed, it may raise an error or cause unexpected behavior.
- If the separator is not found in the input string, the Block will return a list containing the original string as a single element.

## FAQ

???+ question "What happens if the separator is not found in the input string?"
    
    If the separator is not found in the input string, the `SplitString` Block will return a list containing the entire original string as a single element.

???+ question "Can I use multi-character separators?"
    
    Yes, the `SplitString` Block supports multi-character separators. For example, you can set the separator to `" - "` to split a string that contains spaces and hyphens.

???+ question "What happens if the input string is empty?"
    
    If the input string is empty, the `SplitString` Block will return a list containing an empty string: `[""]`.

???+ question "How does the `include_separator` option work?"
    
    If the `include_separator` option is enabled, the separator will be appended to each substring, except for the last one. For example, splitting the string `"apple,banana,cherry"` with a comma separator and `include_separator` enabled will return `["apple,", "banana,", "cherry"]`.