{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `LLM` Block facilitates interaction with a Language Learning Model (LLM) by processing user messages and generating responses. It can handle both simple string responses and structured data based on a defined schema. The block uses a `ModelConfig` to configure the LLM and supports thread history to maintain context across multiple interactions.

{{ generate_block_details_smartspace(page.title) }}

## Example(s)

### Example 1: Generate a simple response from the LLM
- Create an `LLM` Block.
- Set the `llm_config` with the model details and pre-prompt.
- Provide an input message: `"Summarize this document."`
- The Block will use the LLM to generate a text response and send it to the `response` output.

### Example 2: Use a custom response schema
- Set up an `LLM` Block.
- Define a custom `response_schema` that expects an object with specific fields, such as `{"type": "object", "properties": {"summary": {"type": "string"}}}`.
- Provide the input message: `"Summarize the following content."`
- The Block will output the structured response, matching the defined schema.

### Example 3: Use thread history for context
- Create an `LLM` Block with `use_thread_history` set to `True`.
- Provide a series of messages over multiple steps.
- The Block will use the entire conversation history to generate contextually aware responses.

## Error Handling
- If the LLM response does not match the expected schema, the Block will attempt to map the response to the `response_schema`.
- If the schema is not an object and the response is not a string, the Block will raise an error during validation.

## FAQ

???+ question "What happens if the response schema is not provided?"

    If no `response_schema` is provided, the Block assumes the response is a simple string and processes it accordingly.

???+ question "How does the Block handle structured responses?"

    If a structured `response_schema` is defined, the Block expects the LLM to return data that matches the schema. The response is then parsed and sent to the `response` output.

???+ question "Can I use the Block without thread history?"

    Yes, by setting `use_thread_history` to `False`, the Block will only use the current message in its response generation, without considering previous interactions.

???+ question "What happens if the LLM response type is a tool call?"

    If the LLM response is a tool call, the Block will process the tool call arguments and return the result based on the provided schema.