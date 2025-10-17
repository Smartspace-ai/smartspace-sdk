{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview

Performs semantic vector search across multiple datasets within a workspace using embedding-based similarity. Searches across configured dataspaces, interleaves results from multiple datasets, and intelligently truncates output to fit within token limits. Automatically handles result de-duplication, token counting, and property truncation when needed.

## Description

Searches for items in a dataset using vector embeddings and returns the top results based on similarity.

Notes:
- Requires workspace context to access dataspaces and their datasets
- Searches all datasets within specified dataspaces (or all workspace dataspaces if not specified)
- Results are interleaved across datasets to provide diverse results
- Implements intelligent truncation to respect token limits while maximizing information
- Uses the workspace's configured embeddings model for query encoding

## Metadata

- **Category**: Data
- **Label**: vector search, similarity search, embedding search, semantic retrieval, nearest neighbor search

## Configuration Options

| Name | Data Type | Description | Default Value |
|------|-----------|-------------|---------------|
| topn | `int` | Maximum number of results to return across all datasets | `10` |
| token_limit | `int` | Maximum total tokens in the result set (triggers smart truncation if exceeded) | `2000` |
| dataspace_ids | `list[UUID] or Constant(value=None)` | Specific dataspace IDs to search within; if empty/None, searches all workspace dataspaces | `[]` |

## Inputs

| Name | Data Type | Description |
|------|-----------|-------------|
| query | `str` | Semantic search query string to find similar items |

## Outputs

| Name | Data Type | Description |
|------|-----------|-------------|
| results | `list[DataSetItem]` | Top-N most similar items, interleaved from multiple datasets and truncated to fit token limit |

## State Variables

No state variables available.



## Example(s)

### Example 1: Search across all workspace dataspaces
- Config: `topn=10`, `token_limit=2000`, `dataspace_ids=[]`
- Input: `query="machine learning best practices"`
- Output: Up to 10 most relevant items from all datasets in all workspace dataspaces

### Example 2: Search specific dataspaces with higher result count
- Config: `topn=25`, `token_limit=5000`, `dataspace_ids=[uuid1, uuid2]`
- Input: `query="customer feedback analysis"`
- Output: Up to 25 results from datasets in the two specified dataspaces

### Example 3: Constrained token budget
- Config: `topn=50`, `token_limit=1000`
- Input: `query="technical documentation"`
- Output: As many items as fit within 1000 tokens (may be fewer than 50); properties are truncated if needed

### Example 4: Single dataspace focused search
- Config: `topn=5`, `token_limit=3000`, `dataspace_ids=[specific_uuid]`
- Input: `query="quarterly financial reports"`
- Output: Top 5 results from datasets in the single specified dataspace

## Error Handling

- If used outside a workspace context, raises `Exception`
- If no dataspaces are configured or accessible, returns an empty list `[]`
- If no datasets exist in the specified dataspaces, returns an empty list `[]`
- If results exceed `token_limit`, the block applies progressive truncation:
  1. First, includes as many full items as fit
  2. If no full items fit, truncates the top item's properties (strings → halved, lists → halved, dicts → halved)
  3. Ensures at least one result is returned (even if heavily truncated)

## FAQ

???+ question "How does interleaving work?"

    Results from each dataset are interleaved in a round-robin fashion. If you have 3 datasets each returning 10 results, the output cycles through them: item-0 from dataset-1, item-0 from dataset-2, item-0 from dataset-3, item-1 from dataset-1, etc., until `topn` items are collected.

???+ question "What happens when results exceed token_limit?"

    The block uses a multi-stage truncation strategy:
    1. First, it tries to fit as many complete items as possible
    2. If even the top item is too large, it truncates that item's properties (strings, lists, dicts) progressively until it fits
    3. At minimum, one result is always returned

???+ question "How does this differ from SearchDataSet?"

    - **VectorSearch_2_0_0**: Searches across multiple datasets in dataspaces within a workspace; no SQL filtering
    - **SearchDataSet**: Searches a single dataset with SQL-style filters and semantic search combined

???+ question "Can I search a single dataset?"

    Use `SearchDataSet` for single-dataset searches with more control (filtering, pagination). `VectorSearch_2_0_0` is designed for workspace-wide multi-dataset searches.

???+ question "What embedding model is used?"

    The workspace's configured embeddings model (retrieved via the config API) is used for encoding the query.

