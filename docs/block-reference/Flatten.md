{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `Flatten` Block takes a list of lists and flattens it into a single list. It iterates through each sublist and merges all the elements into a single list, removing one level of nesting.

This Block is useful for simplifying nested list structures, making it easier to work with a single list of elements.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Flatten a list of lists of numbers
- Create a `Flatten` Block.
- Provide the input: `[[1, 2], [3, 4], [5, 6]]`.
- The Block will output `[1, 2, 3, 4, 5, 6]`, merging all elements into a single list.

### Example 2: Flatten a list of mixed data types
- Set up a `Flatten` Block.
- Provide the input: `[['apple', 'banana'], ['cherry'], ['date', 'fig']]`.
- The output will be `['apple', 'banana', 'cherry', 'date', 'fig']`, flattening all the sublists into one.

### Example 3: Handle an empty list of lists
- Create a `Flatten` Block.
- Provide an empty list of lists: `[]`.
- The output will be an empty list: `[]`.

## Error Handling
- The `Flatten` Block assumes that the input is a valid list of lists. If the input is not structured as expected (e.g., contains non-list elements), it may raise an error or result in undefined behavior.
- If any sublist is `None`, it will result in an error when trying to flatten the list. Ensure all sublists are properly structured.

## FAQ

???+ question "What happens if one of the sublists is empty?"
    
    If a sublist is empty, the `Flatten` Block will skip over it and continue processing the other sublists. For example, flattening `[[1, 2], [], [3, 4]]` will result in `[1, 2, 3, 4]`.

???+ question "Can I flatten lists with different data types?"
    
    Yes, the `Flatten` Block works with lists containing mixed data types. It will merge all elements, regardless of their types, into a single list.

???+ question "What happens if the input list contains non-list elements?"
    
    The `Flatten` Block expects the input to be a list of lists. If non-list elements are included at the top level, the Block may raise an error or behave unexpectedly. Ensure the input is properly formatted as a list of lists.

???+ question "What if my input list has more than two levels of nesting?"
    
    The `Flatten` Block only flattens the list by one level. If you have multiple levels of nested lists (e.g., `[[[1, 2]], [[3, 4]]]`), you'll need to apply the `Flatten` Block multiple times or use a different approach to fully flatten the structure.