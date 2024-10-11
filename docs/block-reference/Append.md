{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `Append` Block adds a single item to an existing list of items and outputs the updated list. This Block is useful when you need to dynamically add elements to a list during a workflow, ensuring that each new item is properly appended to the existing list.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Append an item to a list of integers
- Create an `Append` Block.
- Provide the input list: `[1, 2, 3]` and an item: `4`.
- The Block will output: `[1, 2, 3, 4]`, adding the item to the end of the list.

### Example 2: Append a string to a list of strings
- Set up an `Append` Block.
- Provide the input list: `["apple", "banana"]` and an item: `"cherry"`.
- The Block will output: `["apple", "banana", "cherry"]`.

### Example 3: Dynamically build a list during a workflow
- Use the `Append` Block in a loop to add multiple items to a list one by one.
- For each iteration, provide the current list and the new item.
- The Block will keep adding each item to the list, resulting in a list with all appended items.

## Error Handling
- If the input `items` is not a list, the Block will raise a `TypeError`.
- The Block assumes that the `item` is of the same type as the elements in `items`.

## FAQ

???+ question "What happens if the input list is empty?"

    If the input list is empty, the Block will create a new list with the single provided item as its content.

???+ question "Can I append different types of items to the list?"

    The Block is generic and expects that all items in the list are of the same type as the item being appended. Mixing types may result in a type error or unexpected behaviour.

???+ question "How does the Block handle large lists?"

    The Block will append items to lists of any size, but keep in mind that extremely large lists may have performance implications depending on the environment and available memory.
