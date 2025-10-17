{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview

## Description

Saves one or more chunk items (dictionaries) to the current dataset scope.

{{ generate_block_details_smartspace(page.title) }}



## Example(s)
 
### Example 1: Save chunk group with dataset ID
- Config: `dataset_id=<your-dataset-uuid>`
- Input `chunks`: a `Chunks` group produced by a chunking block (e.g., SentenceChunk)
- The block merges each chunk’s fields with any extra properties and upserts into the dataset.

### Example 2: Attach extra properties
- Call `save(chunks, source="internal", category="faq")`
- Each stored item includes the chunk fields plus `source` and `category`.

## Error Handling
- If `dataset_id` is missing or invalid, the operation fails.
- For each chunk, the block determines an `id` using `chunk.id` if present; otherwise it generates a UUID. If a provided `id` is not a valid UUID but is a string, it is used as‑is; invalid types raise an error.
- Underlying dataset service errors propagate (e.g., connectivity issues).

## FAQ

???+ question "What is stored for each chunk?"

    The block saves `chunk.model_dump()` merged with any `**properties` you pass, and computes an indexable text value from the combined dictionary.

???+ question "How are IDs assigned?"

    The ID is resolved by checking `id`, `ID`, or `Id` in the merged properties. If none are present, a new UUID is generated.

???+ question "Does this block return any outputs?"

    No. It performs side‑effects by upserting into the dataset. Use dataset query/search blocks to retrieve what was saved.
