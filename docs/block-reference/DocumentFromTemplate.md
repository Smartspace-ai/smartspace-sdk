{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `DocumentFromTemplate` Block converts a string (Markdown, HTML, or other supported formats) to a DOCX document using Pandoc and saves it to blob storage. It provides advanced features including the ability to apply a template file for styling and optionally prepend a cover page to the generated document. This block is ideal for creating professional documents with consistent formatting.

{{ generate_block_details_smartspace(page.title) }}

## Example(s)

### Example 1: Create a simple DOCX document
- Create a `DocumentFromTemplate` Block.
- Set `title` to `"SimpleReport"`.
- Provide input: `"# Report Title\n\n## Section 1\n\nThis is the content of section 1."`
- The Block will convert the Markdown to a DOCX file and save it to blob storage.

### Example 2: Create a document with a custom template
- Create a `DocumentFromTemplate` Block.
- Set `title` to `"StyledReport"`.
- Set `template_file` to a File object pointing to a DOCX template with custom styles.
- Provide input: `"# Annual Report\n\nContent with custom styling applied."`
- The Block will use the template's styles when generating the DOCX file.

### Example 3: Add a cover page to a document
- Create a `DocumentFromTemplate` Block.
- Set `title` to `"ReportWithCover"`.
- Set `cover_page` to a File object pointing to a DOCX file containing a cover page.
- Provide input: `"# Main Content\n\nThis content will appear after the cover page."`
- The Block will merge the cover page with the generated content into a single DOCX file.

### Example 4: Use both template and cover page
- Create a `DocumentFromTemplate` Block.
- Set `title` to `"CompleteReport"`.
- Set `template_file` to a DOCX template for styling.
- Set `cover_page` to a DOCX file with a cover page.
- Provide input content in Markdown format.
- The Block will create a professionally formatted document with cover page and consistent styling.

## Error Handling
- If document conversion fails, the Block will raise an exception with details about the error.
- If the template file or cover page cannot be retrieved from blob storage, an error will be raised.
- If the final document cannot be saved to blob storage, an appropriate error will be raised.

## FAQ

???+ question "What's the difference between template_file and cover_page?"

    - **template_file**: A DOCX file that defines styles, headers, footers, and formatting that will be applied to the generated content. It acts as a style template.
    - **cover_page**: A DOCX file containing actual content (like a title page) that will be prepended to the generated document.

???+ question "What input formats are supported?"

    The Block automatically detects the input format:
    - HTML/HTML5 (detected by `<html` tags)
    - Markdown (detected by `#`, `*`, or `-` markers)
    - ReStructuredText (detected by `..` directives)
    - Defaults to Markdown if the format cannot be determined

???+ question "Can I use this block without a template or cover page?"

    Yes! Both `template_file` and `cover_page` are optional. If neither is provided, the Block will generate a standard DOCX document with default Pandoc styling.

???+ question "How does the document merging work?"

    When a cover page is provided, the Block uses the docxcompose library to properly merge the cover page document with the generated content, preserving formatting, page breaks, and styles from both documents.