{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview

Splits documents into semantically coherent chunks by detecting topic shifts. Uses embeddings to identify natural breakpoints where meaning changes significantly, creating chunks that preserve semantic continuity. Accepts any parent type (File/WebData/generic) and leverages llama-index's `SemanticSplitterNodeParser` with configurable sensitivity thresholds.

## Description

(v2) Semantic chunk parser using SmartSpace models.

Splits a document into semantically related Chunks,
computes embeddings, and emits a ChunkGroup containing them.

Notes:
- Uses embedding similarity to detect semantic breakpoints between text segments
- The `buffer_size` controls how many adjacent sentences are compared together
- The `breakpoint_percentile_threshold` determines sensitivity: higher values = fewer, larger chunks
- Ideal for preserving topical coherence in long documents

## Metadata

- **Category**: Function
- **Label**: semantic chunking v2, meaning-based segmentation, embedding

## Configuration Options

| Name | Data Type | Description | Default Value |
|------|-----------|-------------|---------------|
| buffer_size | `int` | Number of sentences to combine when computing embeddings for breakpoint detection | `1` |
| breakpoint_percentile_threshold | `int` | Percentile threshold (0-100) for semantic similarity; higher values create fewer, larger chunks | `95` |

## Inputs

| Name | Data Type | Description |
|------|-----------|-------------|
| data | `Any` | Parent data (File/WebData/generic) to split into semantic chunks |

## Outputs

| Name | Data Type | Description |
|------|-----------|-------------|
| chunks | `Chunks` | Single `ChunkGroup` containing semantically coherent chunks with preserved parent linkage |

## State Variables

No state variables available.



## Example(s)

### Example 1: Chunk a multi-topic document with default settings
- Config: `buffer_size=1`, `breakpoint_percentile_threshold=95`
- Input: `File` or any parent with multi-paragraph content covering different topics
- Output: `ChunkGroup` where chunks align with topic boundaries rather than arbitrary sizes
- Each chunk name follows pattern `<parent_name>_<index>`

### Example 2: Create more granular chunks with lower threshold
- Config: `buffer_size=1`, `breakpoint_percentile_threshold=85`
- Input: Long document with subtle topic shifts
- Output: More numerous, smaller chunks as the lower threshold detects more breakpoints

### Example 3: Smooth transitions with buffer_size
- Config: `buffer_size=3`, `breakpoint_percentile_threshold=95`
- Input: Technical document with gradual topic evolution
- Output: Chunks respect broader semantic context by comparing 3-sentence windows

## Error Handling

- If the embedding service fails, the error propagates and the block fails
- If input cannot be normalized to text (missing content), raises a runtime error
- Empty or very short text may produce a single chunk or fail if no valid nodes are generated
- The `run_coroutine_sync` helper ensures embeddings work correctly in both sync and async contexts

## FAQ

???+ question "How does semantic chunking differ from token or sentence chunking?"

    Semantic chunking creates variable-sized chunks based on meaning shifts, while token/sentence chunking uses fixed sizes. This preserves topical coherence better for RAG and search applications.

???+ question "What embeddings model is used?"

    The block uses the default embeddings service configured in SmartSpace, wrapped in a llama-index-compatible interface.

???+ question "How do I tune for larger or smaller chunks?"

    Increase `breakpoint_percentile_threshold` (e.g., 98) for fewer, larger chunks. Decrease it (e.g., 90) for more, smaller chunks. Adjust `buffer_size` to control contextual smoothing.

???+ question "Can this work with non-English text?"

    Yes, as long as the underlying embedding model supports the language.

