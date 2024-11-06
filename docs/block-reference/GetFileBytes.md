{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `GetFileBytes` Block retrieves the raw file bytes of a specified file, encoding them as a base64 string. This encoded string is useful for cases where file data needs to be transmitted or processed in a non-binary format, enabling compatibility with various processing tools and APIs.

{{ generate_block_details_smartspace(page.title) }}    

## Example(s)

### Example 1: Retrieve base64-encoded file bytes
- Create a `GetFileBytes` Block.
- Provide a file object as input.
- The Block outputs:
  - `file_bytes_string`: The base64-encoded string representation of the file's raw bytes.
  - `file_name`: The original file name.

### Example 2: Use file bytes for custom processing
- Set up a `GetFileBytes` Block to retrieve the file bytes in base64 format.
- Use the `file_bytes_string` output in downstream blocks or custom processing functions that require file data as a base64 string.

## Error Handling
- If the file cannot be found or accessed, the Block will raise an error.
- If the file URI is invalid, the Block will raise an error during blob retrieval.

## FAQ

???+ question "What types of files are supported?"

    The Block supports any file type accessible through the provided file URI. The bytes are read as-is, making this Block versatile for different file formats.

???+ question "How can I decode the base64 string?"

    You can decode the base64 string back to its original byte format using standard base64 decoding functions in most programming languages.

???+ question "What is the maximum file size supported?"

    The supported file size depends on memory limitations and processing constraints of the environment. Very large files may encounter performance issues or memory limits.

