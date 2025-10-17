{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview

Splits documents into sentence-aware chunks with controlled token limits and overlap. Uses llama-index's `SentenceSplitter` to respect sentence boundaries while maintaining configurable chunk sizes. Supports multi-lingual sentence detection via customizable regex patterns for punctuation. Ideal for maintaining readable, coherent chunks in RAG and NLP applications.

## Description

Parse text into sentence-based chunks, compute embeddings, and preserve original positions.

Notes:
- Accepts any parent type (File/WebData/generic); normalizes to text and preserves the original parent in the emitted `ChunkGroup`.
- Uses llama-index `SentenceSplitter` with configurable separators and overlap.

## Metadata

- **Category**: Function

## Configuration Options

| Name | Data Type | Description | Default Value |
|------|-----------|-------------|---------------|
| chunk_size | `int` | Max tokens per chunk | `200` |
| chunk_overlap | `int` | Overlap between consecutive chunks | `10` |
| separator | `str` | Word separator used by the splitter | ` ` |
| paragraph_separator | `str` | Paragraph delimiter | `\n\n\n` |
| secondary_chunking_regex | `str` | Backup sentence regex (multi-lingual friendly) | `[^,.;。？！]+[,.;。？！]?` |

## Inputs

| Name | Data Type | Description |
|------|-----------|-------------|
| data | `Any` | Parent data (File/WebData/generic) to chunk |

## Outputs

| Name | Data Type | Description |
|------|-----------|-------------|
| chunks | `Chunks` | Single `ChunkGroup` containing sentence-based chunks |

## State Variables

No state variables available.

## Example(s)

### Example 1: Chunk generic content into sentence-preserving chunks
- Provide `data` with `content` containing multiple sentences/paragraphs.
- Configure `chunk_size=200`, `chunk_overlap=10`, custom `paragraph_separator` if needed.
- Output: a `ChunkGroup` with chunks that align to sentence boundaries when possible.
- Each chunk name follows pattern `<parent_name>_<index>`

### Example 2: Multi-lingual content with custom punctuation
- Config: `chunk_size=150`, `chunk_overlap=20`, `secondary_chunking_regex="[^,.;。？！]+[,.;。？！]?"` (includes Chinese punctuation)
- Input: Document with mixed English and Chinese text
- Output: Chunks respect sentence boundaries in both languages

### Example 3: Preserve paragraph structure
- Config: `chunk_size=300`, `chunk_overlap=0`, `paragraph_separator="\n\n\n"`
- Input: Well-structured document with clear paragraph breaks
- Output: Chunks preferentially break at paragraph boundaries when size permits

## Error Handling
If the text cannot be processed by the sentence splitter, a runtime error is raised. Ensure the input can be normalized to text.

## FAQ

???+ question "What if a sentence exceeds chunk_size?"

    The splitter will further split large sentences according to its internal logic and the backup regex.

???+ question "Is punctuation-aware splitting supported?"

    Yes. Use `secondary_chunking_regex` to fine-tune sentence detection, including multi-language punctuation.

