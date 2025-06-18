{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `VectorStore` Block is a comprehensive solution that combines semantic chunking of content with vector storage and search capabilities. It performs semantic chunking to split documents into meaningful segments, generates embeddings for each chunk, and stores them in an in-memory vector database. The block supports uploading new content, updating existing content, and performing similarity searches across the stored chunks.

{{ generate_block_details_smartspace(page.title) }}

## Example(s)

### Example 1: Upload and chunk content
- Create a `VectorStore` Block.
- Use the `upload` step with content: `[{"name": "doc1.txt", "content": "This is a document about AI..."}]`.
- The Block will semantically chunk the content, generate embeddings, and store them in the vector database.
- Returns information about newly uploaded and previously uploaded items.

### Example 2: Search for similar content
- Create a `VectorStore` Block with existing content.
- Use the `search` step with query: `"artificial intelligence"`.
- Set `limit` to `5` to get the top 5 most similar chunks.
- The Block will return chunks ranked by semantic similarity to the query.

### Example 3: Get store information
- Create a `VectorStore` Block.
- Use the `get_store_info` step to retrieve metadata about stored content.
- Returns information about all items in the vector store including content length and chunk counts.

### Example 4: Update existing content
- Create a `VectorStore` Block with existing content.
- Use the `upload` step with updated content for an existing document name.
- The Block will replace the old chunks and embeddings with new ones for that document.

## Error Handling
- If embedding generation fails for content, appropriate errors will be raised.
- The Block handles duplicate content names by updating existing entries.
- Empty or invalid content inputs are handled gracefully.

## FAQ

???+ question "How does semantic chunking work?"

    The Block uses SemanticSplitterNodeParser to group semantically related sentences together. This creates more meaningful chunks compared to simple sentence or token-based splitting, improving the quality of embeddings and search results.

???+ question "What embedding model is used?"

    The Block uses the default embeddings service configured in your SmartSpace instance. This typically provides high-quality vector representations for semantic similarity search.

???+ question "How are search results ranked?"

    Search results are ranked by cosine similarity between the query embedding and stored chunk embeddings. Higher similarity scores indicate more semantically related content.

???+ question "Can I store different types of content?"

    Yes, the Block can handle any text content. The content is automatically processed through semantic chunking regardless of the original format, as long as it's provided as a text string.

???+ question "Is the vector store persistent?"

    The vector store is in-memory and will be reset when the block is reinitialized. For persistent storage, consider using the dedicated vector database blocks or file storage options.