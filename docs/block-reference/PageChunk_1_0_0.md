{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview

Splits page-structured documents into page-range chunks with optional overlap. Supports PDF and PPTX inputs (legacy PPT is not supported). Extracts per‑page (or per‑slide) text and emits a `Chunks` group preserving source metadata.
## Description


Splits documents into page-based chunks with configurable size and overlap.

This block enables users to split large documents (e.g., PDFs) into smaller,
manageable chunks based on page ranges. Supports sequential chunking with
optional overlap between chunks for context preservation.

Example:
- Input: PDF file, start=11, stop=30, chunk_size=5, overlap=1
- Output: Array of 5 file chunks with page ranges:
- Chunk 1: pages 11-15 (5 pages)
- Chunk 2: pages 15-19 (5 pages, overlaps with chunk 1 by 1 page)
- Chunk 3: pages 19-23 (5 pages, overlaps with chunk 2 by 1 page)
- Chunk 4: pages 23-27 (5 pages, overlaps with chunk 3 by 1 page)
- Chunk 5: pages 27-30 (4 pages, overlaps with chunk 4 by 1 page)


## Metadata

- **Category**: Function
- **Label**: page chunking, document splitting, page-based chunks, pdf chunking

## Configuration Options

| Name | Data Type | Description | Default Value |
|------|-----------|-------------|---------------|
| start_page | `int` |  | `1` |
| stop_page | `int` |  | `-1` |
| chunk_size | `int` |  | `5` |
| overlap | `int` |  | `0` |

## Inputs

| Name | Data Type | Description |
|------|-----------|-------------|
| data | `File` |  |

## Outputs

| Name | Data Type | Description |
|------|-----------|-------------|
| chunks | `Chunks` |  |

## State Variables

No state variables available.



## Example(s)

### Example 1: Chunk PDF into 5-page segments with 1-page overlap
- Config: `start_page=1`, `stop_page=-1` (to last), `chunk_size=5`, `overlap=1`
- Input: `File(id="...", name="ebook.pdf")`
- Output: chunk names like `ebook.pdf_pages_1-5`, `ebook.pdf_pages_5-10`, ... with each chunk’s content being the concatenation of the page texts.

### Example 2: Chunk slide deck by slides
- Input: `File(id="...", name="talk.pptx")`
- The block extracts text and tables from each slide, then groups them into slide-range chunks using the same `chunk_size/overlap` policy.
## Error Handling

- If `start_page < 1`, raises `BlockError`.
- If `stop_page <= start_page`, raises `BlockError`.
- If `chunk_size <= 0`, raises `BlockError`.
- If `overlap < 0` or `overlap >= chunk_size`, raises `BlockError`.
- Unsupported file types raise `BlockError` with a list of supported types (`pdf`, `pptx`). Legacy `ppt` is explicitly rejected with a conversion hint.
- If no pages/slides can be extracted, raises `BlockError`.
## FAQ

???+ question "Is page numbering 1‑indexed or 0‑indexed?"

    Configuration (`start_page`, `stop_page`) is 1‑indexed for usability. Internally it is converted to 0‑indexed.

???+ question "How does overlap work?"

    Overlap causes the end of one chunk to share pages with the start of the next chunk. For example, `chunk_size=5` and `overlap=1` produces `1‑5`, `5‑10`, `10‑15`, etc.

???+ question "Why do I see headers like [Page N] or [Slide N]?"

    For clarity, extracted text is prefixed with page/slide headers so downstream chunks remain traceable to their original positions.
