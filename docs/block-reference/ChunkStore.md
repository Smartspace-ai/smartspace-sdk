{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview

In-memory semantic chunk store that:
- Splits or accepts pre-chunked content (via `Chunks`),
- Computes and stores embeddings for each chunk,
- Provides top‑K cosine similarity search across all stored chunks,
- Keeps track of which parent items were just added vs. previously uploaded.

Useful for quick local retrieval without an external vector DB.
## Description


Splits content into semantic chunks, stores their embeddings internally, and
provides cosine-similarity search over stored chunks.


{{ generate_block_details_smartspace(page.title) }}



## Example(s)

### Example 1: Add new chunks and search
- Inputs:
  - `data`: a `Chunks` object (or a list of `Chunks`) produced by upstream chunking blocks.
- Steps:
  1) Call `add_data(data)` to store parents and compute embeddings for all chunks.
  2) Call `semantic_search(query="neural networks")` to retrieve the top `top_k` similar chunks.
- Outputs:
  - `info`: `StoreInfoResponse` containing `just_uploaded` and `previously_uploaded` parents.
  - `chunks`: list of the most similar chunks.

### Example 2: Query a parent by ID
- After `add_data`, take a known parent `id` and call `get_data(id="parent-uuid")`.
- Output: The matching parent object (file/web/generic) or a `GetDataError` if not found.

### Example 3: Get last store info without adding any data
- Call `get_info(run=None)` (the argument is unused).
- Returns the last `StoreInfoResponse` (what was just uploaded and what existed before).

## Error Handling

- `add_data`:
  - Empty input list returns `previously_uploaded` reflecting existing parents.
  - Only supported parent types are retained; unsupported parents are ignored.
  - Any embedding generation error from the embeddings service will propagate and fail the step.
- `semantic_search`:
  - If there are no chunks, returns an empty list.
  - Cosine similarity is computed per chunk; dimensionality mismatches from the embedding service will error.
- `get_data`:
  - If no parent matches the given `id`, returns `GetDataError` with a helpful message.
## FAQ

???+ question "What parent types are supported?"

    File parents (with content), web data parents (complete/with snippet/with summary), and a generic parent type are accepted. Unsupported parent objects are ignored.

???+ question "How does duplicate handling work?"

    Parents are deduplicated by `parent.id`. Re-adding an existing parent lands in `previously_uploaded` and does not duplicate the store.

???+ question "What similarity metric is used?"

    Standard cosine similarity over the stored embedding vectors.

???+ question "How do I clear the store?"

    This block maintains in-memory state. Reinitialize the block (or restart the flow) to reset stored parents, chunks, and embeddings.

???+ question "How many results are returned?"

    Controlled by `top_k` (default 5). Increase it to return more similar chunks.
