{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `Slice` Block is used to extract a portion of a list or string based on configured start and end indexes. The Block slices the input according to these indexes and outputs the sliced result. It can handle both lists and strings, making it versatile for various slicing operations.

By default, the start index is set to `0`, and the end index is set to `0`, which means no slicing will occur unless the indexes are adjusted.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Slice a list of numbers
- Create a `Slice` Block.
- Set the `start` index to `1` and the `end` index to `3`.
- Provide the input list: `[10, 20, 30, 40]`.
- The Block will output `[20, 30]` (elements from index `1` to `3`, not including `3`).

### Example 2: Slice a string
- Set up a `Slice` Block.
- Set the `start` index to `0` and the `end` index to `5`.
- Provide the input string: `"Hello World"`.
- The Block will output `"Hello"`.

### Example 3: Handle an empty slice
- Create a `Slice` Block.
- Leave the default values for `start` and `end`.
- Provide the input list: `[1, 2, 3, 4]`.
- Since the `start` and `end` values are `0`, the Block will return an empty list `[]`.

## Error Handling
- The `Slice` Block expects a valid list or string as input. If an invalid type (such as a number) is provided, the Block may raise an error.
- If the start or end index is out of range, Python's slicing behavior will handle this gracefully by adjusting the slice to fit within the bounds of the input.

## FAQ

???+ question "What happens if the `start` or `end` index is out of range?"
    
    Python handles out-of-range indexes gracefully. If the `start` or `end` index is beyond the length of the input, the Block will adjust the slice to fit within the available items. For example, if the input list has 4 items and the `end` index is set to 10, the Block will return up to the end of the list.

???+ question "Can I use negative indexes for slicing?"
    
    Yes, the `Slice` Block supports negative indexes, which allow you to count from the end of the list or string. For example, setting the `start` index to `-3` and the `end` index to `-1` will slice the last two items from the input.

???+ question "What happens if the `end` index is less than the `start` index?"
    
    If the `end` index is less than the `start` index, the Block will return an empty list or string, as there are no valid items to slice in this range.

???+ question "Can I slice both lists and strings with this Block?"
    
    Yes, the `Slice` Block can handle both lists and strings. It will return a sliced portion of the input, whether it's a list or a string, based on the specified `start` and `end` indexes.