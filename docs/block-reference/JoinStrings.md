{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `JoinStrings` Block takes a list of strings and joins them together into a single string using a configured separator. You can specify the separator to use between the strings (such as a space, comma, or other characters). The resulting string is then output.

This Block is helpful when you need to concatenate a list of strings with a custom separator.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Join strings with a space separator
- Create a `JoinStrings` Block.
- Set the `separator` to `" "`.
- Provide the input list: `["apple", "banana", "cherry"]`.
- The output will be `"apple banana cherry"`.

### Example 2: Join strings with a comma
- Create a `JoinStrings` Block.
- Set the `separator` to `","`.
- Provide the input list: `["apple", "banana", "cherry"]`.
- The output will be `"apple,banana,cherry"`.

### Example 3: Join strings without a separator
- Set up a `JoinStrings` Block.
- Leave the `separator` as an empty string (`""`).
- Provide the input list: `["apple", "banana", "cherry"]`.
- The output will be `"applebananacherry"`.

## Error Handling
- The `JoinStrings` Block expects a list of strings as input. If any item in the list is not a string, it may result in an error or undefined behavior.
- If the input list is empty, the Block will output an empty string.

## FAQ

???+ question "What happens if the input list is empty?"
    
    If the input list is empty, the `JoinStrings` Block will return an empty string.

???+ question "Can I use this block to join strings with multi-character separators?"
    
    Yes, you can use any string as the separator, including multi-character strings. For example, setting the separator to `" - "` will join the strings with a hyphen and spaces.

???+ question "What happens if the input contains non-string items?"
    
    The `JoinStrings` Block expects all items in the list to be strings. If the input contains non-string items, it may raise an error or cause unexpected behavior. Ensure all items are strings before using the Block.