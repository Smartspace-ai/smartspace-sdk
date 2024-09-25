{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `Collect` Block is used to gather data from a channel and store it in a list. Once the channel closes, the Block outputs the collected items as a list.

The `Collect` Block listens for events from an `InputChannel` and appends the incoming data to an internal list (`items_state`). When the channel sends a close event, the collected data is sent out via the `items` output.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Collect data from an input channel
- Create a `Collect` Block.
- Provide an `InputChannel` that sends individual pieces of data.
- As the `InputChannel` sends data, the Block will collect each item.
- When the channel closes, the Block will output the collected list.

### Example 2: Gather event-based data
- Use the `Collect` Block to accumulate data from an event stream.
- For example, during a long-running process, events can be sent via an `InputChannel`.
- Once the process completes and the channel closes, the Block will output the accumulated data as a list of events.

## Error Handling
- The `Collect` Block assumes that data will be available on the channel. If no data is received, the output list will be empty.
- Make sure the channel is properly closed; otherwise, the Block will not output the collected data.

## FAQ

???+ question "What happens if no data is sent before the channel closes?"
    
    If no data is received from the channel before it closes, the `Collect` Block will output an empty list.

???+ question "Can I use this block to collect data from multiple channels?"
    
    The current design of the `Collect` Block focuses on a single channel. To collect data from multiple channels, you'll need to implement additional logic to manage multiple channels.

???+ question "What happens if the channel does not send a close event?"
    
    The `Collect` Block only sends the collected data when it detects a close event. If the channel remains open indefinitely, the collected data will not be outputted.