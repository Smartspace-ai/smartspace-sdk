{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview

Saves chunk collections to the current dataset scope with automatic ID handling and parent metadata preservation. Accepts `Chunks` groups produced by chunking blocks and stores each individual chunk as a dataset item. Supports additional custom properties to be added to every chunk. Requires execution within a dataset context.

## Description

Saves one or more chunk items (dictionaries) to the current dataset scope.

Notes:
- This block operates within a dataset scope (requires dataset context to be active)
- Each chunk in the `Chunks` group is saved as a separate dataset item
- Chunk properties include parent linkage, position, index, and content
- Additional properties can be passed via `**properties` and are merged with chunk data
- Uses upsert semantics: existing chunks (by ID) are updated

{{ generate_block_details_smartspace(page.title) }}



## Example(s)

### Example 1: Save chunks from a token chunker
- Upstream: `TokenChunk_2_0_0` block outputs `Chunks`
- Input: `chunks` = ChunkGroup with 10 token-based chunks
- Result: 10 dataset items are created/updated, one per chunk

### Example 2: Save chunks with additional metadata
- Input: `chunks` = ChunkGroup from `SemanticChunk_2_0_0`
- Provide additional properties: `source="web_scrape"`, `timestamp="2023-10-15"`
- Result: Each chunk is saved with its original properties plus `source` and `timestamp`

### Example 3: Save row chunks from a table
- Upstream: `RowChunk_2_0_0` produces chunks where each content is a JSON row
- Input: `chunks` = ChunkGroup with JSON row chunks
- Result: All row data is persisted to the dataset with parent file linkage

### Example 4: Update existing chunks
- Re-run the same flow with identical chunk IDs
- The block performs upsert: existing chunks are updated with new properties
- No duplicates are created

## Error Handling

- If no `dataset_id` is available in the context service, raises `Exception`
- If chunk properties cannot be serialized, raises an error during `upsert_item`
- ID extraction follows the same logic as `Save` block: checks `id`, `ID`, `Id` keys and generates UUID if missing
- Invalid UUID formats in chunk IDs will raise an exception

## FAQ

???+ question "What's the difference between Save, SaveChunk, and SaveToDataSet?"

    - **Save**: Saves a single item to the current dataset scope
    - **SaveChunk_2_0_0**: Saves multiple chunks (from chunking blocks) to the current dataset scope
    - **SaveToDataSet**: Saves a single item to a specific dataset by ID (no scope required)

???+ question "How are chunk IDs determined?"

    Chunk IDs are extracted from the chunk properties using keys `id`, `ID`, or `Id`. If none exist, a new UUID is generated automatically.

???+ question "Can I save chunks to a specific dataset?"

    This block requires a dataset scope. To save to a specific dataset, use `SaveChunkToDataSet` or configure the dataset context before running the flow.

???+ question "What properties are included in saved chunks?"

    All chunk model fields (`content`, `name`, `index`, `position`, parent linkage, etc.) plus any additional `**properties` passed to the block.

???+ question "Does this support batch operations?"

    Yes, the entire `Chunks` group is processed in one step. Each chunk is saved via an individual upsert call.
