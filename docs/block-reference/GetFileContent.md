{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `GetFileContent` Block extracts text content from a file by determining its type and applying the appropriate extraction method. It supports PDF and other file types, providing a seamless way to handle document files and retrieve their text content.

The block interacts with a `BlobService` to retrieve file data from a URI and processes the content based on the detected file type.

{{ generate_block_details_smartspace(page.title) }}

## Example(s)

### Example 1: Extract text from a PDF file
- Create a `GetFileContent` Block.
- Provide a PDF file via a `File` object.
- The Block will extract the text from the PDF file and output the text content, as well as the file name.

### Example 2: Extract text from a non-PDF file
- Set up a `GetFileContent` Block.
- Provide a text or other non-PDF file via a `File` object.
- The Block will extract and convert the text content using the appropriate method and send it to the `content` output, along with the file name.

## Error Handling
- If the file type is unsupported or processing fails, the block raises an error.
- When converting via Document Intelligence or Pandoc fails, a descriptive error is raised.
- If no file name is available, an empty string is sent to `file_name`.

## FAQ

???+ question "What file types are supported?"

    This Block supports direct reads for: `json`, `html`, `eml`, `ics`, `txt`, `vtt` (and `xlsx` when converting to non-markdown). When `use_document_intelligence` is enabled, it uses Document Intelligence for `pdf`, `docx`, `xlsx`, `pptx`, and common images (`jpg/jpeg/png/bmp/tiff/heif`). Otherwise, Pandoc conversion is used where applicable.

???+ question "What happens if the file type cannot be detected?"

    If the file type cannot be detected, a fallback conversion is attempted where possible; otherwise, an error is raised.

???+ question "How does PDF text extraction work?"

    For PDFs, when not using Document Intelligence, `pypdf` is used to extract text per-page and combined; when Document Intelligence is enabled, content is converted to markdown first.

???+ question "Can I use this block for large files?"

    Yes, but be aware that PDF text extraction can be slow for large or complex documents. For large files, consider handling the text extraction asynchronously to avoid blocking workflows.
