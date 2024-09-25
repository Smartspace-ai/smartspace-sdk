{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `TokenChunk` Block splits a document into chunks based on a fixed token size. This method ensures that each chunk has a consistent number of tokens, making it ideal for cases where precise control over chunk size is necessary, such as when working with models that have specific token limits. However, this method may split sentences or words, which could affect the coherence of the resulting chunks.

This Block uses a tokenizer from the specified model to determine the token size and supports overlapping chunks for better continuity between consecutive chunks.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Chunk a document with default settings
- Create a `TokenChunk` Block.
- Set the `chunk_size` to `200` tokens and `chunk_overlap` to `10`.
- Provide the input text: `"This is a long document that needs to be split into chunks based on tokens."`
- The Block will output chunks of the text, each containing approximately `200` tokens, with an overlap of `10` tokens between consecutive chunks.

### Example 2: Customize the word separator
- Set up a `TokenChunk` Block.
- Set the `separator` to `"\n"` to split text based on newline characters.
- Provide the input text with newline-separated sections: `"Section 1: This is the first section.\nSection 2: This is the second section."`
- The Block will split the text based on newline characters and return token-based chunks.

### Example 3: Handle a list of documents
- Create a `TokenChunk` Block.
- Provide a list of documents to be chunked:
  ```json
  [
    "Document 1: This is the first document.",
    "Document 2: This is the second document."
  ]
  ```
- The Block will chunk each document individually and return the token-based chunks for each one.

## Error Handling
- If the tokenizer cannot be loaded for the specified model, the Block will raise a `RuntimeError` with an appropriate error message.
- If an issue occurs during the chunking process, the Block will raise a `RuntimeError` describing the problem.
- If no valid chunks are created, the Block will return a list containing an empty string.

## FAQ

???+ question "What does the `chunk_size` parameter control?"
    
    The `chunk_size` parameter defines the number of tokens to include in each chunk. This allows you to ensure that each chunk stays within a specified token limit, which can be important for models with token restrictions.

???+ question "What is the purpose of the `chunk_overlap` parameter?"
    
    The `chunk_overlap` parameter specifies the number of tokens that overlap between consecutive chunks. This overlap ensures continuity between chunks, which can be useful for maintaining context in language models.

???+ question "Can I use custom models for tokenization?"
    
    Yes, you can specify a custom model for tokenization by setting the `model_name` parameter. The Block will use the tokenizer from the specified model to split the text into tokens.

???+ question "What happens if the input text is too short to fill a chunk?"
    
    If the input text is shorter than the specified `chunk_size`, the Block will return the text as a single chunk without splitting it. If the text is empty or invalid, the Block will return an empty string.

???+ question "Does this Block ensure that sentences are not split?"
    
    No, the `TokenChunk` Block focuses on creating chunks with a consistent token size. It may split sentences or even words depending on the token boundaries. If you need sentence preservation, consider using a sentence-based chunking method.