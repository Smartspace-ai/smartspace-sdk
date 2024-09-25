{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `Analyzer` Block is designed to process a collection of documents, interact with an LLM (Language Learning Model), and generate a response. It provides tools for summarizing and generating content based on sources and citations from the knowledge base. It ensures that sources used in the response are properly cited.

This block allows customization of the response schema, enabling flexibility in the format of the output (string or structured data).

{{ generate_block_details_smartspace(page.title) }}

## Example(s)

### Example 1: Analyze documents and generate a response
- Create an `Analyzer` Block.
- Set the `response_schema` to `"string"` and configure the `llm_config` for your LLM model.
- Provide a list of documents and a message, such as `"Generate a summary of these documents."`
- The Block will output a response from the LLM, ensuring that sources are cited appropriately.

## Error Handling
- If the LLM response is null, an `LLMError` will be raised.
- If the response type is unexpected, an exception will be raised.
- If there is an issue with JSON content formatting, the Block will attempt to fix the escaping, but will raise a runtime error if unable to process it.

## FAQ

???+ question "What happens if the response schema is not a string?"

    If the response schema is not a string, the block will expect the content to be returned in JSON format, with citations appropriately placed using a different format from string-based responses.

???+ question "How does the block ensure sources are properly cited?"

    The block automatically replaces placeholders like `(source_1)` with citations in the output content, ensuring all cited sources are included in the final response.

???+ question "Can I use custom LLM configurations?"

    Yes, you can configure the `llm_config` to match your desired LLM model. The Block supports custom pre-prompts and other LLM configurations.
