{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `Map` Block is designed to iterate through a list of items and process each item using a configured tool. The results from processing each item are collected and outputted as a list once all items have been processed.

The Block works generically with any input type (`ItemT`) and any result type (`ResultT`), making it versatile for various use cases where a list of items needs to be transformed or processed individually.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Process a list of numbers
- Create a `Map` Block.
- Configure the `run` operation to multiply each number by 2.
- Provide the input list: `[1, 2, 3, 4]`.
- The `Map` Block will process each number, applying the multiplication, and output `[2, 4, 6, 8]`.

### Example 2: Map over a list of strings
- Set up a `Map` Block.
- Configure the `run` operation to append "processed" to each string.
- Provide the input list: `["item1", "item2"]`.
- The output will be `["item1 processed", "item2 processed"]` after processing.

### Example 3: Use with an async operation
- Create a `Map` Block that performs an asynchronous operation, such as fetching data from an API.
- Provide a list of IDs as the input: `[123, 456, 789]`.
- The `Map` Block will process each ID, fetch data from the API, and return the results as a list.

## Error Handling
- If the input list is empty, the `Map` Block will return an empty list without processing any items.
- The `Map` Block tracks the processing of each item. If there is an issue while processing a specific item (e.g., a failure in the `run` operation), the result for that item may remain unprocessed unless handled.
- Ensure that the `run` operation is configured correctly to avoid errors during processing.

## FAQ

???+ question "What happens if an error occurs during the `run` operation?"
    
    If an error occurs during the `run` operation, the `Map` Block will not stop the entire process. Instead, it will continue processing the remaining items in the list. You may need to handle errors in the `run` operation to ensure robust behavior.

???+ question "Can I use this block to process items asynchronously?"
    
    Yes, the `Map` Block supports asynchronous operations. The `run` operation can be configured to perform async tasks, and the Block will await the results before continuing to the next item.

???+ question "How can I track the progress of the mapping operation?"
    
    The Block provides an internal `count` state that tracks how many items remain to be processed. You can use this state to monitor the progress of the operation.