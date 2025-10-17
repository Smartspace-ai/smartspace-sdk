{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview

Creates overlapping sentence windows for enhanced context in retrieval applications. Each chunk contains a center sentence plus configurable surrounding sentences, ensuring every chunk has rich local context. Uses llama-index's `SentenceWindowNodeParser` to build windowed segments. Ideal for question-answering and semantic search where context around key information is critical.

## Description


(v2) Sentence window chunk parser for all parent types.

Splits a document into windowed sentence Chunks,
computes embeddings, and emits a ChunkGroup for File, WebData, or generic inputs.


Notes:
- Accepts any parent type (File/WebData/generic); normalizes to text and preserves original parent.
- Uses llama-index `SentenceWindowNodeParser` to build windowed chunks.

## Metadata

- **Category**: Function
- **Label**: window chunk v2, sentence windowing, embedding

## Configuration Options

| Name | Data Type | Description | Default Value |
|------|-----------|-------------|---------------|
| window_size | `int` | Number of sentences to include on each side of the center sentence | `3` |

## Inputs

| Name | Data Type | Description |
|------|-----------|-------------|
| data | `Any` | Parent data (File/WebData/generic) to window-chunk |

## Outputs

| Name | Data Type | Description |
|------|-----------|-------------|
| chunks | `Chunks` | Single `ChunkGroup` containing sentence-window chunks |

## State Variables

No state variables available.



## Example(s)

### Example 1: Window chunk with size 2
- Configure `window_size=2`.
- Input: long text content; call `chunk(data=...)`.
- Output: each chunk contains `2` sentences before and after the center sentence (5 sentences total per chunk).

### Example 2: Maximum context for dense documents
- Config: `window_size=5`
- Input: Dense technical or legal document where understanding requires significant context
- Output: Each chunk contains 11 sentences (5 before + center + 5 after), providing rich context for retrieval

### Example 3: Minimal window for faster processing
- Config: `window_size=1`
- Input: Simple FAQ or short-form content
- Output: Each chunk contains 3 sentences (1 before + center + 1 after)

## Error Handling

- If the sentence window parser fails to process the text, a runtime error is raised
- If input cannot be normalized to text, raises an error
- Short documents with fewer sentences than the window size will still be chunked, but windows will be truncated at boundaries

## FAQ

???+ question "Do chunks overlap?"

    Yes—by definition, sliding windows overlap to preserve local context. Adjacent chunks share sentences in their windows.

???+ question "How is this different from SentenceChunk with overlap?"

    WindowChunk ensures every chunk has symmetric context (N sentences before and after), while SentenceChunk creates chunks of token size that may have asymmetric overlap.

???+ question "What happens at document boundaries?"

    At the start and end of documents, windows are naturally smaller since there are no sentences beyond the boundaries.

???+ question "What metadata is preserved in chunks?"

    Each chunk includes `window` (the full windowed text), `original_sentence` (the center sentence), plus parent linkage, index, and position.

