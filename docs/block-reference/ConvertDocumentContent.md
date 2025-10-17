{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview

## Description

Converts file content to another format using pandoc or Azure Document Intelligence

## Metadata

- **Category**: Data
- **Obsolete**: True
- **Use_instead**: GetFileContent
- **Deprecated_reason**: This block will be removed in a future version. Use the `GetFileContent` block instead
- **Label**: file conversion, document conversion, format transformation, content transformation, document formatting

## Configuration Options

| Name | Data Type | Description | Default Value |
|------|-----------|-------------|---------------|
| to_format | `PandocToFormats` |  | `PandocToFormats.MARKDOWN` |
| use_document_intelligence | `bool` |  | `True` |

## Inputs

| Name | Data Type | Description |
|------|-----------|-------------|
| file | `File` |  |

## Outputs

| Name | Data Type | Description |
|------|-----------|-------------|
| output | `str` |  |

## State Variables

No state variables available.



## Example(s)

## Error Handling

## FAQ

