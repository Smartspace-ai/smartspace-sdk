{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview

Indexes file contents into an in-memory vector store and supports semantic search over chunked content.
- Converts supported file types to text (via Document Intelligence or Pandoc),
- Uses a pluggable chunking Tool (`chunk`) to split content,
- Embeds and stores chunks per file,
- Exposes outputs with all files and newly added files,
- Provides APIs to get raw content by filename and to search similar chunks.
## Description


Store and search embeddings in an in-memory vector database.

Args:
top_k: The number of results to return in search.

Steps:
1: Update index with embeddings.
2: Search index to return relevant documents.



## Metadata

- **Category**: Function
- **Label**: file store, file embedding, file search, file vector database, file vector store, file vector search

## Configuration Options

| Name | Data Type | Description | Default Value |
|------|-----------|-------------|---------------|
| top_k | `int` |  | `5` |
| use_document_intelligence | `bool` |  | `True` |

## Inputs

| Name | Data Type | Description |
|------|-----------|-------------|
| files | `list[File]` |  |
| filename | `str` |  |
| query | `str` |  |

## Outputs

| Name | Data Type | Description |
|------|-----------|-------------|
| all_files | `list[FileInfo]` |  |
| files | `list[FileInfo]` |  |
| file_content | `str` |  |
| chunks | `list[str]` |  |

## State Variables

| Name | Data Type | Description |
|------|-----------|-------------|
| data | `Any` |  |
| files_state | `list[ChunkedFile]` |  |
| pending_file_count | `int` |  |
| all_files_state | `list[FileInfo]` |  |
| new_files_state | `list[FileInfo]` |  |



## Example(s)

### Example 1: Add files and list newly added entries
- Inputs:
  - `files`: `[File(id=..., name="report.pdf"), File(id=..., name="slides.pptx")]`
- Call `add_files(files)`.
- Outputs:
  - `files`: list of `FileInfo` for just-added files
  - `all_files`: cumulative list of `FileInfo` for all processed files

### Example 2: Retrieve a file’s full content
- Call `get(filename="report.pdf")`.
- Returns the stored text content for that file.

### Example 3: Semantic search over all chunks
- Call `semantic_search(query="revenue growth")`.
- Returns up to `top_k` relevant chunk texts across all indexed files.
## Error Handling

- `add_files`:
  - Ignores files previously processed (deduplicated by file `id`).
  - If content extraction fails, raises a `BlockError` with the file name.
  - Conversion pathways:
    - If `use_document_intelligence` is true and extension ∈ {pdf, pptx, docx, xlsx} → convert via Document Intelligence to markdown.
    - Else if extension is Pandoc‑supported → convert via Pandoc to markdown.
- `get`:
  - Returns a friendly message if no file with the given `filename` was indexed.
- `semantic_search`:
  - If there are no chunks indexed, returns an empty list.
  - Embedding/shape issues from the embeddings service propagate.
## FAQ

???+ question "How do I control chunking granularity?"

    Provide a `chunk` Tool implementation on the block that splits text content into your desired chunk size and format. The block invokes this tool per file.

???+ question "What file types are supported?"

    - With Document Intelligence: pdf, pptx, docx, xlsx
    - With Pandoc: any format supported by your Pandoc installation (converted to markdown first)

???+ question "How are duplicates handled?"

    Files are deduplicated by `id`. Re‑adding the same `id` won’t re‑process content.

???+ question "What does `top_k` control?"

    The maximum number of most similar chunks returned for `semantic_search` (default 5).
