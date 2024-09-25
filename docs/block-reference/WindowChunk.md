{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `WindowChunk` Block splits a document into chunks where each chunk consists of a central sentence and its surrounding sentences based on a defined window size. This method captures context by including a specified number of sentences before and after the central sentence, ensuring that each chunk provides a windowed view of the text.

This Block is particularly useful when you need to maintain local context around sentences, such as for tasks like summarization, entity extraction, or contextual analysis.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Chunk a document with a window of 3 sentences
- Create a `WindowChunk` Block.
- Set the `window_size` to `3` (each chunk will include 3 sentences before and after the central sentence).
- Provide the input text: 
  ```
  "Sentence 1. Sentence 2. Sentence 3. Sentence 4. Sentence 5. Sentence 6. Sentence 7."
  ```
- The Block will output chunks, such as:
  ```json
  [
    "Sentence 1. Sentence 2. Sentence 3.",
    "Sentence 2. Sentence 3. Sentence 4.",
    "Sentence 3. Sentence 4. Sentence 5.",
    "Sentence 4. Sentence 5. Sentence 6.",
    "Sentence 5. Sentence 6. Sentence 7."
  ]
  ```

### Example 2: Use a custom window size
- Set up a `WindowChunk` Block.
- Set the `window_size` to `2`.
- Provide the input text: 
  ```json
  "The sky is blue. The sun is shining. The birds are singing. It's a beautiful day."
  ```
- The Block will output windowed chunks, such as:
  ```json
  [
    "The sky is blue. The sun is shining.",
    "The sun is shining. The birds are singing.",
    "The birds are singing. It's a beautiful day."
  ]
  ```

### Example 3: Handle multiple documents
- Create a `WindowChunk` Block.
- Provide a list of documents as input:
  ```json
  [
    "Document 1: Sentence 1. Sentence 2.",
    "Document 2: Sentence 1. Sentence 2. Sentence 3."
  ]
  ```
- The Block will process each document and return windowed chunks for both:
  ```json
  [
    ["Sentence 1. Sentence 2."],
    ["Sentence 1. Sentence 2.", "Sentence 2. Sentence 3."]
  ]
  ```

## Error Handling
- If the input text is invalid or an error occurs during chunking, the Block will raise a `RuntimeError` with a descriptive error message.
- If no valid chunks are generated, the Block will return a list containing an empty string.

## FAQ

???+ question "What does the `window_size` parameter control?"
    
    The `window_size` parameter specifies how many sentences before and after the central sentence should be included in each chunk. A larger window size provides more context for each chunk, while a smaller window size results in tighter sentence groups.

???+ question "What happens if the document is too short to fill a chunk?"
    
    If the document is shorter than the specified window size, the Block will return smaller chunks that include only the available sentences. For example, if a document has 2 sentences and the window size is 3, the Block will still return the entire document in one chunk.

???+ question "Can I use this Block for multiple documents at once?"
    
    Yes, the `WindowChunk` Block can process a list of documents. Each document will be split into windowed chunks independently, and the Block will return the results for each document as a list of chunks.

???+ question "Does this Block ensure that sentences are not split?"
    
    Yes, the `WindowChunk` Block is designed to preserve complete sentences. It chunks the text based on full sentences, ensuring that no sentence is split across chunks.