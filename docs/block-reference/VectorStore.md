{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
Semantic chunking + in-memory vector search for generic content. Splits text into semantically coherent chunks, embeds them, and stores embeddings for cosine-similarity search. Supports incremental uploads and retrieving raw content by name.

{{ generate_block_details_smartspace(page.title) }}

## Example(s)

### Example 1: Add content and get store info
- Call `add_data(data=[{"name":"doc1.txt","content":"This is a document about AI..."}])`.
- The block chunks and embeds, then returns `store_info` summarizing newly vs previously uploaded items.

### Example 2: Semantic search over stored chunks
- Call `semantic_search(query="artificial intelligence")`.
- Output: `search_chunks` list containing the top `top_k` most similar chunk texts.

### Example 3: Retrieve raw content by name
- Call `get(query_name="doc1.txt")`.
- Output: `get_content` returns the original text content or a friendly message if not found.

### Example 4: Incremental uploads
- Add more items via `add_data` later. `store_info` differentiates `just_uploaded` vs `previously_uploaded`.

## Error Handling
- Chunking errors raise a runtime error.
- Empty inputs to `add_data` return a summary without adding.
- Unknown names in `get` return a friendly not-found string.

## FAQ

???+ question "What chunking method is used?"

    Uses llama-index `SemanticSplitterNodeParser`, tuned by `buffer_size` and `breakpoint_percentile_threshold`.

???+ question "How many search results are returned?"

    Controlled by `top_k` (default 5).

???+ question "How are `just_uploaded` vs `previously_uploaded` determined?"

    Based on the names added during the latest `add_data` call compared to content already in the store.

???+ question "Is storage persistent?"

    No. This block uses in-memory state. Reinitialize to clear. For persistence, use dataset/vector DB blocks.
