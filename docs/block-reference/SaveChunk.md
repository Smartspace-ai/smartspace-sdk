{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `SaveChunk` Block saves one or more chunk items (dictionaries) to the current dataset scope. It's designed to handle chunk data from text processing, document parsing, or data extraction operations. The block can save either a single chunk dictionary or a list of chunk dictionaries, automatically handling ID generation and merging with additional properties.

{{ generate_block_details_smartspace(page.title) }}

## Example(s)

### Example 1: Save a single chunk
- Create a `SaveChunk` Block.
- Provide a chunk dictionary: `{"text": "This is chunk content", "index": 0, "source": "document.pdf"}`.
- Add additional properties: `category="text"`, `processed=True`.
- The Block will merge the chunk data with additional properties and save to the current dataset.

### Example 2: Save multiple chunks from text processing
- Create a `SaveChunk` Block.
- Provide a list of chunks from a chunking operation.
- Add metadata properties: `document_id="123"`, `processing_date="2023-01-01"`.
- The Block will save each chunk individually with the merged properties.

### Example 3: Save chunks with custom IDs
- Create a `SaveChunk` Block.
- Provide chunks that include `id` fields: `[{"id": "chunk_1", "content": "..."}]`.
- The Block will use the provided IDs instead of generating new ones.

### Example 4: Save processed document chunks
- Create a `SaveChunk` Block in a dataset processing flow.
- Receive chunks from a text chunking block.
- Add processing metadata: `model_version="v2.1"`, `timestamp="2023-12-01"`.
- All chunks will be saved with the additional metadata.

## Error Handling
- If no dataset_id is available in the current scope, the Block will raise an exception.
- Invalid UUID formats in chunk `id` fields will raise appropriate errors.
- The Block handles both single dictionaries and lists of dictionaries seamlessly.

## FAQ

???+ question "What's the difference between SaveChunk and Save?"

    - **SaveChunk**: Specifically designed for chunk data, handles both single chunks and lists of chunks
    - **Save**: General-purpose saving for any properties, saves one item at a time
    
    Use SaveChunk when working with text processing or chunking operations.

???+ question "How does ID handling work?"

    The Block looks for `id`, `ID`, or `Id` fields in chunk data:
    - If found, validates the UUID format and uses it
    - If not found, generates a new UUID automatically
    - Each chunk gets its own unique ID when saving multiple chunks

???+ question "Can I add metadata to all chunks?"

    Yes! Any additional properties provided to the Block are merged with each chunk before saving. This is useful for adding processing metadata, source information, or categorization.

???+ question "What data types are supported in chunks?"

    Chunks support any JSON-serializable data including:
    - Strings, numbers, booleans
    - Nested objects and arrays  
    - Null values
    - Date strings

???+ question "Does this work outside dataset scope?"

    No, SaveChunk requires a dataset scope to operate. It uses the current dataset context to determine where to save the chunks. Use SaveToDataSet if you need to specify a particular dataset ID.