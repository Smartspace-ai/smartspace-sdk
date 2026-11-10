{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `DocumentCreator` Block converts strings or files to various document formats using Pandoc. It supports a wide range of input formats including Markdown, HTML, ReStructuredText, LaTeX, and many others, and can output to formats like DOCX, PDF, ODT, EPUB, HTML, RTF, JSON, PPTX, and Markdown. The block automatically detects the input format when processing strings and can handle existing files from blob storage, converting them to the desired output format.

{{ generate_block_details_smartspace(page.title) }}

## Example(s)

### Example 1: Convert a Markdown string to a Word document
- Create a `DocumentCreator` Block.
- Set `output_file_type` to `FileType.DOCX`.
- Set `title` to `"MyDocument"`.
- Provide input: `"# Hello World\n\nThis is a **markdown** document."`
- The Block will convert the Markdown to a DOCX file and save it to blob storage.

### Example 2: Convert an HTML string to PDF
- Create a `DocumentCreator` Block.
- Set `output_file_type` to `FileType.PDF`.
- Set `title` to `"WebReport"`.
- Provide input: `"<html><body><h1>Report</h1><p>Content here</p></body></html>"`
- The Block will detect HTML format and convert it to a PDF file.

### Example 3: Convert an existing file to a different format
- Create a `DocumentCreator` Block.
- Set `output_file_type` to `FileType.EPUB`.
- Provide a File object from blob storage (e.g., a DOCX file).
- The Block will fetch the file, extract its content, and convert it to EPUB format.

### Example 4: Convert a CSV file to PDF
- Create a `DocumentCreator` Block.
- Set `output_file_type` to `FileType.PDF`.
- Provide a CSV File object.
- The Block will read the CSV content and convert it to a formatted PDF document.

## Error Handling
- If document conversion fails, the Block will raise an exception with details about the error.
- If an input file cannot be found in blob storage, an error will be raised.
- If the converted file is empty or cannot be saved to blob storage, appropriate errors will be raised.
- For PDF generation, the Block uses xelatex as the PDF engine. Ensure LaTeX is properly configured if PDF output is required.

## FAQ

???+ question "What input formats are supported?"

    The Block supports numerous input formats including:
    - Markdown (various flavors: CommonMark, GitHub, MultiMarkdown, etc.)
    - HTML/HTML5
    - ReStructuredText (RST)
    - LaTeX
    - DocBook XML
    - MediaWiki, Textile, Jira, Org mode
    - AsciiDoc, EPUB, Confluence, TWiki
    - And many more through Pandoc

???+ question "How does the Block detect the input format?"

    For string inputs, the Block automatically detects the format by examining the content:
    - HTML is detected by the presence of `<html` tags
    - Markdown is detected by common markers like `#`, `*`, or `-` at the start
    - ReStructuredText is detected by `..` directives
    - If unknown, it defaults to Markdown

???+ question "Can I convert from any file type?"

    The Block supports various file types including:
    - Documents: DOCX, PDF, TXT, CSV, TSV
    - Presentations: PPTX
    - Spreadsheets: XLSX
    - Web formats: HTML, JSON
    - Email formats: EML, ICS
    
    For unsupported formats, the Block will attempt to use the document converter service.

???+ question "What's the difference between DocumentCreator and DocumentConverterFromFile?"

    `DocumentConverterFromFile` is deprecated and should not be used. `DocumentCreator` is the modern replacement that handles both string inputs and file inputs in a single block, making it more versatile and easier to use.