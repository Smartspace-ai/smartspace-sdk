{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `VectorSearch` Block performs a vector-based search over specified data spaces using embeddings to find the most relevant documents or items based on input queries. It uses an embeddings service to transform the input queries into vector embeddings, and searches for documents within the token limit and data space constraints.

This Block is useful for retrieving relevant documents from large datasets using semantic search methods, and it supports token limits to ensure the search results are manageable within model constraints.

{{ generate_block_details_smartspace(page.title) }}

## Example(s)

### Example 1: Perform a vector search with default parameters
- Create a `VectorSearch` Block.
- Provide a list of queries, such as `["Find documents about AI ethics."]`.
- The Block will return the top 10 most relevant search results from the available data spaces, ranked by relevance.

### Example 2: Search across multiple data spaces
- Set up a `VectorSearch` Block.
- Provide a list of `dataspace_ids` to specify which data spaces to search through.
- Provide a list of queries, such as `["Machine learning in healthcare."]`.
- The Block will perform a vector search across the provided data spaces and return the top search results.

### Example 3: Search with a custom token limit
- Create a `VectorSearch` Block.
- Set the `token_limit` to `1000`.
- Provide a list of queries: `["AI and automation in manufacturing."]`.
- The Block will return search results while ensuring that the total token count for the results stays under the specified limit.

## Error Handling
- If the workspace is not defined, the Block will raise an error indicating that it can only be used within a workspace.
- If no results are found within the token limit, the Block will return an empty list.

## FAQ

???+ question "What happens if the token limit is exceeded?"

    The Block will stop adding results once the token limit is reached. Any results that would cause the token count to exceed the limit will be excluded from the final output.

???+ question "Can I search across multiple data spaces?"

    Yes, you can specify multiple `dataspace_ids` to search across different data spaces. If no `dataspace_ids` are provided, the search will be performed in the default data spaces associated with the workspace.

???+ question "What happens if the query returns too many results?"

    The Block will sort the results by relevance (score) and return only the top results based on the `topn` parameter, which defaults to 10.

???+ question "How does the Block handle duplicate results?"

    The Block checks for duplicates based on the document `id` and merges content from duplicate paths, ensuring that the final results are unique and comprehensive.