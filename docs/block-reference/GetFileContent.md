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
- If the file type is not detected or cannot be processed, the Block will raise an error.
- PDF text extraction may be slower for large or complex documents due to the nature of the PDF structure.
- If no file name is available, an empty string will be sent to the `file_name` output.

## FAQ

???+ question "What file types are supported?"

    This Block supports PDF files and other file types that can be partitioned and converted to text. It uses specialized methods for extracting text from PDFs and more general methods for other file types.

???+ question "What happens if the file type cannot be detected?"

    If the file type cannot be detected, the Block will use a fallback method to handle the file, or it will raise an error if the file type is unsupported.

???+ question "How does PDF text extraction work?"

    PDF text extraction uses the `pypdf` library to extract text from each page. The extracted text is then combined into a single string separated by double newlines for readability.

???+ question "Can I use this block for large files?"

    Yes, but be aware that PDF text extraction can be slow for large or complex documents. For large files, consider handling the text extraction asynchronously to avoid blocking workflows.
