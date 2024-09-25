{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `LLMSelect` Block is designed to interact with a Language Learning Model (LLM) and present a list of options based on a user’s input. The LLM evaluates the input message and selects one of the predefined options based on the description of each option. This Block is useful for scenarios where the LLM needs to make decisions between different possible actions or tools.

{{ generate_block_details_smartspace(page.title) }}

## Example(s)

### Example 1: Use LLM to select an option
- Create an `LLMSelect` Block.
- Define options such as `"Option1: Perform Action A"` and `"Option2: Perform Action B"`.
- Provide an input message: `"Which action should I take?"`.
- The Block will use the LLM to analyze the message and select the appropriate option based on the provided descriptions.

### Example 2: Use thread history in decision-making
- Set up an `LLMSelect` Block with `use_thread_history` set to `True`.
- Provide a series of messages or a conversation history.
- The Block will use the entire thread history when making the decision, ensuring that the context of the conversation is maintained.

## Error Handling
- If the LLM settings are unexpectedly `None`, an exception will be raised.
- If the LLM response does not match any of the predefined options, the Block will raise an exception.

## FAQ

???+ question "What happens if the LLM cannot choose an option?"

    If the LLM's response does not match any of the available options, the Block will raise an exception. Ensure that the option descriptions are clear and distinguishable.

???+ question "Can I use the LLMSelect Block with multiple options?"

    Yes, you can define multiple options in the `options` dictionary. Each option has a description that helps guide the LLM in making its selection.

???+ question "How does the Block use thread history?"

    If `use_thread_history` is set to `True`, the Block will include previous messages in the conversation as part of the LLM's decision-making process. This helps maintain context when selecting an option.

???+ question "What happens if the LLM response is ambiguous?"

    The Block checks the LLM's response against the available options in descending order of length to find a match. If the response does not match any option, an exception is raised.