{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `SentenceChunk` Block parses text with a preference for keeping complete sentences and paragraphs together. This Block aims to create chunks of text that maintain sentence integrity, making it useful for tasks where meaningful text divisions are important, such as summarization or token-limited models.

The Block uses a combination of sentence splitting, token counting, and customizable chunk sizes and overlaps. It also supports a secondary chunking regex for additional control over sentence splitting.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Chunk a document with default settings
- Create a `SentenceChunk` Block.
- Set the `chunk_size` to `200` tokens and `chunk_overlap` to `10`.
- Provide the input text: `"This is the first sentence. This is the second sentence. This is the third sentence."`
- The Block will output chunks, keeping sentences together while staying within the token limit, such as:
  ```json
  [
    "This is the first sentence. This is the second sentence.",
    "This is the second sentence. This is the third sentence."
  ]
  ```

### Example 2: Use a custom paragraph separator
- Set up a `SentenceChunk` Block.
- Set the `paragraph_separator` to `"\n\n"`.
- Provide a text input with paragraphs separated by double newlines:
  ```json
  "Paragraph one text.\n\nParagraph two text."
  ```
- The Block will chunk the paragraphs based on the provided separator.

### Example 3: Handle complex sentence structures with custom regex
- Create a `SentenceChunk` Block.
- Set the `secondary_chunking_regex` to `"[.!?]+"` to split based on sentence-ending punctuation.
- Provide the input: `"Complex sentences can have multiple clauses; splitting them requires attention to detail."`
- The Block will split the text at appropriate points while maintaining sentence integrity.

## Error Handling
- If the tokenizer cannot be loaded for the specified model, the Block will raise a `RuntimeError` with an appropriate error message.
- If an issue occurs during chunking, the Block will raise a `RuntimeError` describing the problem.

## FAQ

???+ question "What does the `chunk_size` parameter do?"
    
    The `chunk_size` parameter controls the number of tokens that each chunk should contain. The Block attempts to keep chunks within this size while preserving complete sentences and paragraphs.

???+ question "What is the `chunk_overlap` parameter?"
    
    The `chunk_overlap` parameter specifies the number of tokens that should overlap between consecutive chunks. This ensures that no important information is lost at chunk boundaries.

???+ question "Can I customize the separators used for splitting text?"
    
    Yes, you can customize both the `separator` for splitting words and the `paragraph_separator` for splitting paragraphs. By default, the word separator is a space (`" "`), and the paragraph separator is `"\n\n\n"`.

???+ question "What happens if no valid chunks are created?"
    
    If no valid chunks are created, the Block will return a list containing an empty string to indicate that no meaningful chunks were generated from the input text.

???+ question "Can I use a custom model for tokenization?"
    
    Yes, you can specify a custom model for tokenization by setting the `model_name` parameter. The Block will use the specified model's tokenizer to encode the text into tokens.
