{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `SearchDataSet` Block searches dataset items with advanced SQL-style filtering capabilities combined with full-text semantic search. It provides comprehensive search features including semantic search across dataset content, SQL-style property filtering with full operator support, complex logical expressions, multi-datatype support, multiple query support for comprehensive coverage, and flexible pagination. The block converts SQL-style filter expressions directly to Cosmos DB queries for optimal performance.

{{ generate_block_details_smartspace(page.title) }}

## Example(s)

### Example 1: Simple semantic search
- Create a `SearchDataSet` Block.
- Set `dataset_id` to your target dataset's UUID.
- Provide query: `"machine learning algorithms"`.
- The Block will return items that semantically match the search query.

### Example 2: Search with filtering
- Create a `SearchDataSet` Block.
- Set `dataset_id` to your dataset's UUID.
- Provide query: `"data science"`.
- Set `filter` to `"Type = 'Document' AND createdAt >= '2023-01-01'"`.
- The Block will search for "data science" content but only return documents created after 2023.

### Example 3: Multiple query search
- Create a `SearchDataSet` Block.
- Provide query as a list: `["artificial intelligence", "neural networks", "deep learning"]`.
- The Block will search for all three terms and return deduplicated results.

### Example 4: Complex filtered search with pagination
- Create a `SearchDataSet` Block.
- Provide query: `"quarterly report"`.
- Set `filter` to `"(Department = 'Finance' OR Department = 'Sales') AND Status = 'Published'"`.
- Set `skip` to `10` and `take` to `20`.
- The Block will return items 11-30 matching both the search and filter criteria.

## Error Handling
- If the Block is used outside of a workspace context, it will raise an exception.
- If no dataset_id is provided or the dataset is not found in the workspace, it returns an empty list.
- Empty query lists will return an empty result list.
- Invalid SQL syntax in filter expressions will raise appropriate parsing errors.

## FAQ

???+ question "How does semantic search work?"

    The Block performs semantic/vector search on the indexed content of dataset items. It finds items that are conceptually similar to your query, not just exact text matches. This means searching for "car" might also find items about "automobile" or "vehicle".

???+ question "Can I search multiple queries at once?"

    Yes! You can provide either:
    - A single query string: `"search term"`
    - A list of queries: `["term1", "term2", "term3"]`
    
    When using multiple queries, the Block automatically deduplicates results.

???+ question "What's the difference between SearchDataSet and GetDataSet?"

    - **SearchDataSet**: Performs semantic/full-text search first, then applies filters
    - **GetDataSet**: Only filters based on exact property matches without search
    
    Use SearchDataSet when you need to find content by meaning, and GetDataSet when you know exact property values.

???+ question "What SQL operators are supported in filters?"

    Same as GetDataSet:
    - **Comparison**: `=`, `!=`, `<>`, `>`, `>=`, `<`, `<=`
    - **IN operator**: `Type IN ['Document', 'Image', 'Video']`
    - **NULL checks**: `Description = null`, `Tags != null`
    - **Logical**: `AND`, `OR`, with parentheses for grouping

???+ question "How are results ordered?"

    Results are ordered by relevance to the search query. The most semantically similar items appear first. When using multiple queries, items matching earlier queries may appear before items matching later queries, though deduplication ensures each item appears only once.