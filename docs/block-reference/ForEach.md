{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `ForEach` Block is used to loop through a list of items and output each item one at a time. It takes a list of any type (`list[ItemT]`) as input, and for each item in the list, it sends the item through an output channel. Once all items are processed, the output channel is closed.

This Block is ideal for cases where items need to be processed individually rather than in a batch.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Loop through a list of numbers
- Create a `ForEach` Block.
- Provide the input list: `[10, 20, 30]`.
- The `ForEach` Block will output each number (`10`, `20`, `30`) one at a time.

### Example 2: Process a list of strings
- Set up a `ForEach` Block.
- Provide a list of strings: `["apple", "banana", "cherry"]`.
- The Block will output each string individually as `"apple"`, `"banana"`, and `"cherry"`.

### Example 3: Handle an empty list
- Create a `ForEach` Block.
- Provide an empty list: `[]`.
- Since the list is empty, the Block will not output any items but will close the channel immediately.

## Error Handling
- The `ForEach` Block expects a list as input. If the provided input is not a list, it may result in undefined behavior or errors.
- If the list is empty, the Block will simply close the output channel without sending any items.

## FAQ

???+ question "What happens if the list is empty?"
    
    If the list is empty, the `ForEach` Block will not send any items and will immediately close the output channel.

???+ question "Can I use the `ForEach` Block with asynchronous operations?"
    
    The `ForEach` Block can send items through an output channel, which can then be consumed by other blocks that handle asynchronous operations. However, the `ForEach` Block itself does not perform any asynchronous processing on the items.

???+ question "Can I use the `ForEach` Block with nested lists?"
    
    The `ForEach` Block will treat each item in the list as an individual item, even if the item itself is a list. To iterate over nested lists, additional logic may be needed.