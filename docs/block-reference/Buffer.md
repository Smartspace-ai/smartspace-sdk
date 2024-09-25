{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `Buffer` Block temporarily stores values in a list and releases them one by one when the block is ready. This allows for buffering of data to control the flow of values in a sequence. The block holds incoming values until a signal is received to process the next one. It ensures that only one value is processed at a time, allowing better control over sequential workflows.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Buffering values and processing them one by one
- Create a `Buffer` Block.
- Send values sequentially using the `value()` step, such as `buffer.value(10)` and `buffer.value(20)`.
- Use the `next()` step to signal that the buffer is ready to process the next value.
- The Block will output each value in sequence, processing one at a time.

### Example 2: Processing multiple values in a controlled manner
- Set up a `Buffer` Block to collect multiple incoming values.
- Use the `value()` step to send values into the buffer: `buffer.value("A")`, `buffer.value("B")`.
- Use `next()` to release values sequentially, ensuring that each value is handled one by one before the next is processed.

## Error Handling
- If the buffer is not ready, the `next()` step will not process any values until the Block signals readiness.
- If the buffer is empty, no value will be sent when `next()` is called.

## FAQ

???+ question "What happens if I call `next()` when the buffer is empty?"

    If there are no values in the buffer, calling `next()` will not send any output, and the Block will simply remain ready to process new values.

???+ question "Can I add multiple values to the buffer?"

    Yes, you can append multiple values to the buffer by calling the `value()` step repeatedly. The buffer will store all the values and release them one by one as `next()` is called.

???+ question "How does the block handle readiness?"

    The Block uses a `ready` flag to control when it is ready to release the next value from the buffer. It becomes ready once the previous value has been processed and `next()` has been called.

