{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `SemanticChunk` Block is used to split a document into semantic chunks, with each chunk being a group of semantically related sentences. The Block utilizes an embedding model to evaluate the semantic similarity between sentences and decides when to form a new chunk based on a configurable dissimilarity threshold.

This Block is useful for breaking down large documents into smaller, meaningful sections for tasks like summarization, topic modeling, or information extraction.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Split a document into chunks
- Create a `SemanticChunk` Block.
- Set the `buffer_size` to `2` (group sentences in batches of 2).
- Set the `breakpoint_percentile_threshold` to `90`.
- Provide the input text: `"The quick brown fox jumps over the lazy dog. This is a test sentence. Semantic chunking is a powerful tool."`
- The Block will output a list of chunks, such as:
  ```json
  [
    "The quick brown fox jumps over the lazy dog. This is a test sentence.",
    "Semantic chunking is a powerful tool."
  ]
  ```

### Example 2: Handle a list of documents
- Set up a `SemanticChunk` Block.
- Provide a list of text documents:
  ```json
  [
    "Document 1: The sky is blue.",
    "Document 2: The sun is bright."
  ]
  ```
- The Block will split each document into semantic chunks and return the result:
  ```json
  [
    "Document 1: The sky is blue.",
    "Document 2: The sun is bright."
  ]
  ```

### Example 3: Use a custom embedding model
- Set the `model_name` to `"custom/embedding-model"` to use a specific embedding model for chunking.
- Provide the text to be chunked: `"This is a test for using a custom model."`
- The Block will use the custom model for embedding and chunking the text.

## Error Handling
- If the input text is invalid or there is an error during the chunking process, the Block will raise a `RuntimeError` with a descriptive error message.
- If no chunks are generated, the Block will return a list containing an empty string.

## FAQ

???+ question "What does the `buffer_size` parameter do?"
    
    The `buffer_size` parameter determines the number of sentences that are grouped together when evaluating semantic similarity. A higher buffer size will result in larger chunks, while a smaller buffer size will create more granular chunks.

???+ question "What is the `breakpoint_percentile_threshold`?"
    
    The `breakpoint_percentile_threshold` is the percentile of cosine dissimilarity that must be exceeded between a group of sentences and the next to form a new chunk. A lower threshold will create more chunks, while a higher threshold will create fewer, larger chunks.

???+ question "Can I use a custom embedding model for semantic chunking?"
    
    Yes, you can specify a custom embedding model by setting the `model_name` parameter to the name of the model you want to use. The default model is `"BAAI/bge-small-en-v1.5"`.

???+ question "What happens if no semantic chunks are created?"
    
    If no semantic chunks are created, the Block will return a list containing an empty string to indicate that no meaningful chunks were found.