{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview

Batch processes multiple files by converting them to a specified format and maintains state to avoid reprocessing. Uses Azure Document Intelligence for supported formats (pdf, docx, pptx) and Pandoc for others. Outputs a cumulative list of all processed file contents, making it ideal for incremental document processing pipelines.

## Description

Converts multiple files to a specified format and outputs their contents as a list. Keeps track of processed files to avoid reprocessing.

Notes:
- Maintains internal state (`processed_files`) to track already-processed files by ID
- Only processes new files in subsequent calls, avoiding redundant conversions
- Uses Document Intelligence when enabled for pdf, docx, pptx formats
- Falls back to Pandoc for other supported file types
- Outputs cumulative list of all processed content (not just new files)

## Metadata

- **Category**: Data
- **Label**: bulk file conversion, batch document processing, multi-file content extraction, document list generation

## Configuration Options

| Name | Data Type | Description | Default Value |
|------|-----------|-------------|---------------|
| to_format | `PandocToFormats` | Target output format for all files (e.g., MARKDOWN, HTML, PLAIN) | `PandocToFormats.MARKDOWN` |
| use_document_intelligence | `bool` | Enable Azure Document Intelligence for PDF, DOCX, PPTX files (higher quality extraction) | `True` |

## Inputs

| Name | Data Type | Description |
|------|-----------|-------------|
| files | `list[File]` | List of file objects to convert (only new files are processed) |

## Outputs

| Name | Data Type | Description |
|------|-----------|-------------|
| output | `list[str]` | Cumulative list of converted content strings for all processed files (includes previously processed files) |

## State Variables

| Name | Data Type | Description |
|------|-----------|-------------|
| processed_files | `list[indexedContent]` | Internal state tracking file IDs and their converted content to prevent reprocessing |



## Example(s)

### Example 1: Convert multiple PDFs to markdown
- Config: `to_format=MARKDOWN`, `use_document_intelligence=True`
- Input call 1: `files=[file1.pdf, file2.pdf]`
- Output: List of 2 markdown strings
- Input call 2: `files=[file1.pdf, file2.pdf, file3.pdf]`
- Output: List of 3 markdown strings (file1 and file2 are not reprocessed)

### Example 2: Batch convert documents to HTML
- Config: `to_format=HTML`, `use_document_intelligence=True`
- Input: `files=[report.docx, slides.pptx, data.xlsx]`
- Output: List of 3 HTML strings representing each document's content

### Example 3: Process files with Pandoc only
- Config: `to_format=MARKDOWN`, `use_document_intelligence=False`
- Input: `files=[doc1.txt, doc2.html, doc3.md]`
- Output: List of 3 markdown strings (all converted via Pandoc)

### Example 4: Incremental file addition
- Config: defaults
- Input call 1: `files=[a.pdf]` → Output: `["content_of_a"]`
- Input call 2: `files=[a.pdf, b.pdf]` → Output: `["content_of_a", "content_of_b"]`
- Input call 3: `files=[b.pdf, c.pdf]` → Output: `["content_of_a", "content_of_b", "content_of_c"]`

## Error Handling

- If a file conversion fails, the error is caught and logged but does not stop processing of other files
- Failed files are not added to `processed_files` state, allowing retry in subsequent calls
- File pointer is reset (`.seek(0)`) before Pandoc conversion to ensure complete content reading
- If no new files are provided (all already processed), returns the existing cumulative content list

## FAQ

???+ question "Why does output include previously processed files?"

    The block maintains state and returns a cumulative list of all processed files, not just new ones. This makes it easy to track the complete set of converted documents across multiple calls.

???+ question "What happens if I send the same file list multiple times?"

    Only new files (not in `processed_files` state) are converted. Previously processed files are skipped, and the output includes all content.

???+ question "How is this different from GetFileContent?"

    - **GetFileContent**: Processes a single file per call, no state tracking
    - **GetFiles**: Processes multiple files, maintains state to avoid reprocessing, outputs cumulative list

???+ question "What formats are supported?"

    - With Document Intelligence: pdf, docx, pptx (high-quality extraction)
    - With Pandoc: Any format Pandoc supports (txt, html, md, docx, pdf, etc.)
    - Output format is controlled by `to_format` config

???+ question "Can I clear the processed files state?"

    The state persists within the block instance. To reset, you would need to reinitialize the block or implement custom state management.

???+ question "What happens when a file fails to process?"

    The error is logged, the file is skipped, and other files continue processing. The failed file is not added to state, so it will be retried in the next call.

