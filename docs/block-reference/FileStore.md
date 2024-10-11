{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing(height=None, width=250) }}
{% endif %}

## Overview
The `FileStore` Block manages the storage and retrieval of files, allowing for content chunking, embedding generation, and semantic search over the stored files. It uses an in-memory vector database to store the embeddings of file chunks, enabling quick and efficient search based on the semantic similarity between a query and the stored content.

This Block is useful for applications that require storing documents, generating embeddings for content, and performing similarity-based searches over stored text.

{{ generate_block_details_smartspace(page.title) }}

## Example(s)

### Example 1: Add files and store their content
- Create a `FileStore` Block.
- Provide a list of files to the `add_files()` step.
- The Block will extract content from each file, convert it into chunks, generate embeddings, and store the results.
- The `all_files` output will contain information about all stored files, and the `files` output will contain details about the newly added files.

### Example 2: Retrieve file content by filename
- Set up a `FileStore` Block with files already added.
- Use the `get()` step with a specific filename, such as `"document1.txt"`.
- The Block will return the full content of the specified file.

### Example 3: Perform a semantic search over stored content
- Use a `FileStore` Block with stored file content and embeddings.
- Provide a query, such as `"Find information about AI ethics."` to the `semantic_search()` step.
- The Block will return the most relevant chunks of content based on the semantic similarity between the query and stored chunks.

## Error Handling
- If a file is not found when calling the `get()` step, the Block will return a message indicating that the file was not found.
- If no valid chunks are returned for a file, the Block will handle the missing content gracefully.
- If an unsupported file format is provided, the Block will process the file using a default content extraction method.

## FAQ

???+ question "How does the Block handle different file formats?"

    The Block can process files in various formats, including converting certain files to markdown using Pandoc. Unsupported formats are processed using default extraction methods.

???+ question "Can I perform searches on large document collections?"

    Yes, the Block is designed to handle large collections of documents by storing content in chunks and generating embeddings for each chunk. Semantic search allows for efficient querying across large datasets.

???+ question "What happens if I add the same file multiple times?"

    The Block treats each file addition independently. If the same file is added multiple times, it will be processed and stored as separate entries.

???+ question "How does semantic search work?"

    The Block generates an embedding for the input query and compares it with the embeddings of stored chunks using cosine similarity. The top `k` most similar chunks are returned based on the `top_k` configuration.

