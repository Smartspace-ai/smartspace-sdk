{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview

## Description

Get's the raw file bytes of a file, saved as a base64 encoded string. Useful for custom processing.

## Metadata

- **Category**: Data
- **Obsolete**: True
- **Use_instead**: GetFileContent
- **Deprecated_reason**: This block will be removed in a future version. Use the `GetFileContent` block instead
- **Label**: file bytes, encoded file, base64 encoded file, file content, file binary data

## Configuration Options

No configuration options available.

## Inputs

| Name | Data Type | Description |
|------|-----------|-------------|
| file | `File` |  |

## Outputs

| Name | Data Type | Description |
|------|-----------|-------------|
| file_bytes_string | `str` | Base64 encoded string of the file bytes |
| file_name | `str` | Name of the file |

## State Variables

No state variables available.



## Example(s)

## Error Handling
 - If the file cannot be read from blob storage, an error is raised.
 - Large files are supported; output is base64-encoded to a string.

## FAQ
???+ question "Why is this block marked obsolete?"

    Prefer `GetFileContent` which handles content extraction and conversions. `GetFileBytes` remains for cases where raw bytes are required.

