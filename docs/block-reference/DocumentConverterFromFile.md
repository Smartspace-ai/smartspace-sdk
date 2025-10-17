{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview

## Description

Retrieves an existing file from blob storage, converts it to a specified document format (Word, PDF, ODT, EPUB, etc.) using Pandoc, and saves the converted file back to blob storage.

## Metadata

- **Category**: Data
- **Obsolete**: True
- **Use_instead**: DocumentCreator
- **Deprecated_reason**: This block will be removed in a future version. Use the `DocumentCreator` block instead
- **Label**: document conversion, file transformation, format conversion, content processing, document formatting

## Configuration Options

| Name | Data Type | Description | Default Value |
|------|-----------|-------------|---------------|
| output_file_type | `FileType` |  | `FileType.DOCX` |

## Inputs

| Name | Data Type | Description |
|------|-----------|-------------|
| file | `File` |  |

## Outputs

| Name | Data Type | Description |
|------|-----------|-------------|
| result | `File` |  |

## State Variables

No state variables available.



## Example(s)

## Error Handling

## FAQ

