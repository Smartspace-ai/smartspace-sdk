{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
!!! warning "Deprecated Block"
    This block is deprecated and will be removed in a future version. Prefer wiring the `sources` output of your LLM block directly to your flow response instead of using this helper.

The `CreateResponseWithSources` Block generates an API response that includes both the content and associated sources, useful when returning content with references to where information was derived.

This Block ensures that sources are appropriately formatted, allowing them to be provided either as a list of `Source` objects or as a single URI string.

{{ generate_block_details_smartspace(page.title) }}

## Example(s)

### Example 1: Create a response with a list of sources
- Create a `CreateResponseWithSources` Block.
- Provide content such as `"Here is the summary of the report."` and a list of sources: `[Source(index=1, uri="https://example.com/source1"), Source(index=2, uri="https://example.com/source2")]`.
- The Block will emit an API response containing the content and the list of sources.

### Example 2: Create a response with a single source path/URI
- Set up a `CreateResponseWithSources` Block.
- Provide content: `"This is the generated content."` and a single source URI: `"https://example.com/source"`.
- The Block will convert the URI into a `Source` object and output the response with the source.

### Example 3: Create a response without any sources
- Create a `CreateResponseWithSources` Block.
- Provide content: `"Content without sources."` and no sources.
- The Block will output the content with an empty sources array.

## Error Handling
- If `sources` is a string, it is converted to a single `Source(index=1, container_item_path=<string>)`.
- If no sources are provided, an empty list is sent.

## FAQ

???+ question "What happens if I provide a string instead of a list of sources?"

    If a single string is provided, the Block will convert the string into a `Source` object with an index of `1` and include it in the response.

???+ question "Can I create a response without any sources?"

    Yes, if no sources are provided, the Block will generate a response with an empty list for the `sources` field.

???+ question "Does this Block handle non-string content?"

    Yes, the Block automatically converts non-string content (e.g., dictionaries) into a JSON string using `json.dumps()` before sending it in the response.
