{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `First` Block retrieves the first item from a given list. It takes a list of any type as input and outputs the first element. If the list is empty, it may raise an error due to attempting to access an index that does not exist.

This Block is useful when you need to quickly access the first item in a list for further processing.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Get the first item in a list of numbers
- Create a `First` Block.
- Provide the input list: `[10, 20, 30]`.
- The Block will output `10`, the first element in the list.

### Example 2: Get the first item in a list of strings
- Set up a `First` Block.
- Provide the input list: `["apple", "banana", "cherry"]`.
- The Block will output `"apple"`, the first string in the list.

### Example 3: Handle an empty list
- Create a `First` Block.
- Provide an empty list: `[]`.
- The Block will raise an error since there is no first item to return.

## Error Handling
- The `First` Block will raise an `IndexError` if the input list is empty. Ensure that the list contains at least one item before using this Block.
- The Block assumes that the input is a valid list. If the input is not a list, it may result in undefined behavior or raise an error.

## FAQ

???+ question "What happens if the list is empty?"
    
    If the list is empty, the `First` Block will raise an `IndexError` because there is no item at index `0`. You should ensure that the list contains at least one item before using the Block.

???+ question "Can I use the `First` Block with different data types in the list?"
    
    Yes, the `First` Block works with lists containing any data type. It will return the first item, regardless of its type.

???+ question "What if I want to return the first item safely without an error?"
    
    To avoid errors when the list is empty, you can add a check before using the `First` Block. Alternatively, you can modify the Block to return `None` or a default value if the list is empty.