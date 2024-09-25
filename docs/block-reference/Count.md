{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `Count` Block is designed to count the number of items in a given list. It takes a list of any type (`list[Any]`) as input and returns the number of elements in that list as an integer.

This Block is useful when you need to know the size of a collection before proceeding with further operations.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Count items in a list
- Create a `Count` Block.
- Provide the input list: `[1, 2, 3, 4, 5]`.
- The `Count` Block will output `5`, the number of elements in the list.

### Example 2: Count items in a list of strings
- Create a `Count` Block.
- Provide the input list: `["apple", "banana", "cherry"]`.
- The output will be `3` since there are three items in the list.

### Example 3: Handle an empty list
- Set up a `Count` Block.
- Provide an empty list as input: `[]`.
- The `Count` Block will return `0` as there are no items in the list.

## Error Handling
- The `Count` Block expects a list as input. If an invalid type (e.g., a non-list) is provided, the behavior may be undefined or raise an error.
- An empty list will result in an output of `0`.

## FAQ

???+ question "What happens if the input is not a list?"
    
    The `Count` Block expects a list as input. If a non-list type is provided, it may raise an error or result in undefined behavior. Ensure the input is a valid list.

???+ question "Can I use the `Count` Block to count elements in a nested list?"
    
    No, the `Count` Block will return the count of the top-level items in the list. It will not recursively count elements inside nested lists.

???+ question "What happens if the list contains mixed data types?"
    
    The `Count` Block can handle lists with mixed data types. It simply counts the number of items regardless of their types.