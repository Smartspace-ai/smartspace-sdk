{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `ConvertDocumentContent` Block converts the content of a file to a specified format using Pandoc. This Block is useful for transforming documents into various formats (e.g., Markdown, HTML) to support diverse processing and display requirements.

{{ generate_block_details_smartspace(page.title) }}

## Example(s)

### Example 1: Convert a document to Markdown
- Create a `ConvertDocumentContent` Block.
- Set the `to_format` configuration to `PandocToFormats.MARKDOWN`.
- Provide a file as input.
- The Block will output the file’s content converted to Markdown.

### Example 2: Convert a PDF to HTML for web display
- Set up a `ConvertDocumentContent` Block.
- Set `to_format` to `PandocToFormats.HTML`.
- Provide a PDF file as input.
- The Block will output the content converted to HTML, suitable for embedding in a webpage.

## Error Handling
- If the file cannot be accessed or is in an unsupported format, the Block will raise an error.
- If the `to_format` conversion is invalid or unsupported by Pandoc, the Block will raise an error.

## FAQ

???+ question "What file formats are supported?"

    The Block supports any format that Pandoc can read and convert. Common formats include Markdown, HTML, PDF, and DOCX. Check Pandoc’s documentation for a full list of supported formats.

???+ question "How can I customize the output format?"

    You can set the `to_format` configuration to the desired output format, such as `PandocToFormats.HTML` or `PandocToFormats.MARKDOWN`.

???+ question "What happens if the file is too large?"

    Very large files may encounter performance issues or memory constraints, depending on the environment’s capabilities. For best results, test with smaller files if possible.
