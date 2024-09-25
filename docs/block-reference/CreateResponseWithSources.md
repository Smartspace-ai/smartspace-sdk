{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `CreateResponseWithSources` Block is used to generate an API response that includes both the content and associated sources. This is particularly useful when you want to return content along with references to the sources from which the information was derived.

This Block ensures that sources are appropriately formatted, allowing them to be provided either as a list of `Source` objects or as a single URI string.

{{ generate_block_details_smartspace(page.title) }}

## Example(s)

### Example 1: Create a response with a list of sources
- Create a `CreateResponseWithSources` Block.
- Provide content such as `"Here is the summary of the report."` and a list of sources: `[Source(index=1, uri="https://example.com/source1"), Source(index=2, uri="https://example.com/source2")]`.
- The Block will emit an API response containing the content and the list of sources.

### Example 2: Create a response with a single source URI
- Set up a `CreateResponseWithSources` Block.
- Provide content: `"This is the generated content."` and a single source URI: `"https://example.com/source"`.
- The Block will convert the URI into a `Source` object and output the response with the source.

### Example 3: Create a response without any sources
- Create a `CreateResponseWithSources` Block.
- Provide content: `"Content without sources."` and no sources.
- The Block will output the content with an empty sources array.

## Error Handling
- If the sources input is a string, the Block will automatically convert it into a `Source` object with the default index of `1`.
- If no sources are provided, the Block will send an empty list as the `sources` field in the response.

## FAQ

???+ question "What happens if I provide a string instead of a list of sources?"

    If a single string is provided, the Block will convert the string into a `Source` object with an index of `1` and include it in the response.

???+ question "Can I create a response without any sources?"

    Yes, if no sources are provided, the Block will generate a response with an empty list for the `sources` field.

???+ question "Does this Block handle non-string content?"

    Yes, the Block automatically converts non-string content (e.g., dictionaries) into a JSON string using `json.dumps()` before sending it in the response.