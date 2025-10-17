{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview

Loads a file’s bytes from blob storage, extracts text content using Azure Document Intelligence (for supported types) or Pandoc, and emits a `FileWithContent` with `id`, `name`, and extracted `content`. Optionally converts the output to a target format via `convert_to`.
## Description


Loads a file and its content, optionally converting it to a specified format.
Uses document intelligence for supported formats. Supports VTT (WebVTT) subtitle and caption files.

### Common supported file types
- PDF (.pdf)
- Word (.docx)
- Excel (.xlsx)
- PowerPoint (.pptx)
- Text (.txt)
- HTML (.html)
- VTT (.vtt)
- JPEG (.jpg, .jpeg)
- PNG (.png)
- json (.json)
- markdown (.md)

For the full list of supported types and details, see the documentation.


## Metadata

- **Category**: Data
- **Label**: file content extraction, document processing, content extraction, file conversion, text extraction, vtt, webvtt, subtitles, captions

## Configuration Options

| Name | Data Type | Description | Default Value |
|------|-----------|-------------|---------------|
| convert_to | `PandocToFormats` |  | `PandocToFormats.MARKDOWN` |
| use_document_intelligence | `bool` |  | `True` |

## Inputs

| Name | Data Type | Description |
|------|-----------|-------------|
| file | `File` |  |

## Outputs

| Name | Data Type | Description |
|------|-----------|-------------|
| files_with_content | `FileWithContent` |  |

## State Variables

No state variables available.



## Example(s)

### Example 1: Extract markdown from a PDF
- Config: `use_document_intelligence=True`, `convert_to=MARKDOWN`
- Input: `File(id="...", name="whitepaper.pdf")`
- Output: `files_with_content` with markdown text of the PDF.

### Example 2: Keep JSON as JSON
- Config: `convert_to=MARKDOWN` (default) but input is a `.json` file.
- Behavior: raw JSON is preserved when target is markdown.

### Example 3: Convert HTML to plain markdown
- Config: `convert_to=MARKDOWN`
- Input: `File(id="...", name="index.html")`
- Output: markdown text content from the HTML file.
## Error Handling

- If the file type is unsupported or content extraction fails, sends an error message through `error` with details and still returns a `FileWithContent` containing the error text.
- For binary outputs from blob storage, content is decoded as UTF‑8 with `errors="ignore"`.
- When requested conversion fails, a descriptive reason is included in the error message.
## FAQ

???+ question "Which formats use Document Intelligence vs. Pandoc?"

    - Document Intelligence (when enabled): pdf, docx, xlsx, pptx, jpg, jpeg, png, bmp, tiff, heif
    - Pandoc path (and other direct reads): json, html, eml, ics, txt, vtt, xlsx (when converting to non‑markdown)

???+ question "Why are JSON files preserved when converting to markdown?"

    The block avoids lossy conversion for JSON to keep data fidelity if the target is markdown.

???+ question "What does `convert_to` affect?"

    If set, output content is converted to that target format (e.g., markdown, html, etc.) after initial extraction.
