{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `LLMDataEnrich` Block uses a Language Learning Model (LLM) to enrich documents with additional information based on user-defined instructions, outputting structured data according to a specified schema. It extracts and categorizes information from input text into specified fields, where each field can contain multiple relevant entries as a list of strings. This block is particularly useful for entity extraction, data parsing, and enriching unstructured content with structured metadata.

{{ generate_block_details_smartspace(page.title) }}

## Example(s)

### Example 1: Extract entities from a document
- Create an `LLMDataEnrich` Block.
- Set `field_names` to `["people", "organizations", "locations"]`.
- Configure the `llm_config` with appropriate model settings.
- Provide input text: `"John Smith from Microsoft visited the Seattle office yesterday."`
- The Block will extract: `{"people": ["John Smith"], "organizations": ["Microsoft"], "locations": ["Seattle"]}`.

### Example 2: Parse product information
- Create an `LLMDataEnrich` Block.
- Set `field_names` to `["product_names", "prices", "features"]`.
- Provide input: `"The iPhone 15 Pro costs $999 and features a titanium design with 5x zoom camera."`
- The Block will extract structured data for each field.

### Example 3: Extract multiple values per field
- Create an `LLMDataEnrich` Block.
- Set `field_names` to `["skills", "certifications", "experience_years"]`.
- Provide a resume or CV as input.
- The Block will extract multiple skills, certifications, and experience mentions as lists.

### Example 4: Process content items with files
- Create an `LLMDataEnrich` Block.
- Configure with desired extraction fields.
- Provide a list of `ContentItem` objects or a single `ContentItem`.
- The Block will process the content and extract structured information according to the schema.

## Error Handling
- If the LLM does not return a tool call response, the Block will raise a `BlockError`.
- If the LLM returns empty arguments for the tool call, an error will be raised.
- The Block validates that responses match the expected schema structure.
 - When using a non-object response schema, ensure your downstream expects a string, as the block unwraps the `response` field.

## FAQ

???+ question "How are the extraction fields defined?"

    Fields are defined in the `field_names` list. Each field name becomes a property in the output schema, with the type `list[str]` to allow multiple values per field.

???+ question "What types of input does the Block accept?"

    The Block accepts:
    - Simple strings
    - Single `ContentItem` objects
    - Lists of `ContentItem` objects
    
    ContentItems can include text and file references.

???+ question "Can I customize the extraction behavior?"

    Yes, through the `llm_config` you can:
    - Set a custom pre-prompt to guide extraction
    - Choose different LLM models
    - Configure model parameters
    - Enable thread history for context-aware extraction

???+ question "Why are all fields lists of strings?"

    This design allows maximum flexibility - each field can contain zero, one, or multiple extracted entities. For example, a document might mention multiple people, locations, or dates. The list structure accommodates all these cases.

???+ question "How does this differ from the standard LLM block?"

    While the standard LLM block can output structured data, LLMDataEnrich is specifically optimized for entity extraction and data enrichment tasks. It automatically creates the appropriate schema based on field names and uses tool calling to ensure structured output.
### Example 5: Dynamic schema with empty fields
- If `field_names=[]`, the dynamic model creates an empty object schema.
- The LLM may return `{}` when no fields are requested; add fields to `field_names` to guide extraction.

### Example 6: Non-object response schema
- When `response_schema` is not an object (e.g., `{"type":"string"}`), the tool’s parameter schema wraps the result under `response`. The block then unwraps `args["response"]`.
- Use this when you prefer a single string output rather than a multi-field object.

### Example 7: Large inputs and token limits
- The block calls `remove_excess_tokens_chat_request` to trim oversize requests.
- If content is long, consider chunking upstream and enriching per chunk to improve reliability.
???+ question "What happens if there are no matches for a field?"

    The corresponding list will be empty. You can post-process empty lists as needed, or instruct the model to return `[]` explicitly when nothing is found.
