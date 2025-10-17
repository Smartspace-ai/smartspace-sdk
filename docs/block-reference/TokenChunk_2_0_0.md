{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview

Splits documents into fixed-size token-based chunks with configurable overlap. Uses llama-index's `TokenTextSplitter` to create chunks of consistent token length, making it ideal for LLM applications with strict context limits. Unlike sentence-based chunking, this may split mid-sentence to maintain precise token counts. Accepts any parent type (File/WebData/generic) and preserves linkage to source.

## Description

(v2) Token-based chunk parser for all parent types.

Splits a document into Chunks of fixed token size (with overlap), then emits a single ChunkGroup containing all of them, honoring File, WebData, or generic inputs.

Notes:
- Accepts any parent type (File/WebData/generic); the block normalizes to text and preserves original parent linkage in the emitted `ChunkGroup`.
- Uses llama-index `TokenTextSplitter` under the hood.

## Metadata

- **Category**: Function
- **Label**: token chunk v2, text splitting, document chunking

## Configuration Options

| Name | Data Type | Description | Default Value |
|------|-----------|-------------|---------------|
| chunk_size | `int` | Max tokens per chunk | `200` |
| chunk_overlap | `int` | Overlapping tokens between adjacent chunks | `10` |
| separator | `str` | Word separator (reserved) | ` ` |

## Inputs

| Name | Data Type | Description |
|------|-----------|-------------|
| data | `Any` | Parent data (File/WebData/generic) to chunk |

## Outputs

| Name | Data Type | Description |
|------|-----------|-------------|
| chunks | `Chunks` | Single `ChunkGroup` containing all token chunks |

## State Variables

No state variables available.

## Example(s)

### Example 1: Chunk a File parent
- Input: a `File` with textual content.
- Call `chunk(data=file)`.
- Output: a `ChunkGroup` where each chunk tracks its `index`, `position`, and is linked to the file parent.

### Example 2: Chunk generic string content
- Provide a simple object with `content` and optional `name`.
- Call `chunk(data={"name": "doc-1", "content": long_text})`.
- Output: `ChunkGroup` with chunk names derived from the parent name and indices.

### Example 3: Maximum overlap for context preservation
- Config: `chunk_size=200`, `chunk_overlap=50`
- Input: Technical documentation where context is critical
- Output: Each chunk shares 50 tokens with adjacent chunks, improving retrieval continuity

### Example 4: Strict size limits for LLM processing
- Config: `chunk_size=512`, `chunk_overlap=0`
- Input: Large corpus to process with a specific model's context window
- Output: Every chunk has exactly (or up to) 512 tokens with no overlap

## Error Handling
If an internal error occurs during tokenization/chunking, the block raises a runtime error. Ensure the input can be normalized to text.

## FAQ

???+ question "Does this preserve sentence boundaries?"

    No. Token-based splitting may break sentences. If you need sentence coherence, use `SentenceChunk_2_0_0`.

???+ question "How are chunk names assigned?"

    `name` defaults to `<parent_name>_<index>` if a parent name/title exists; otherwise indices are used.

