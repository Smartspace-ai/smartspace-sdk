{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview

## Description


Splits content into semantic chunks, stores their embeddings internally, and
provides cosine-similarity search over stored chunks.


## Metadata

- **Category**: Function
- **Label**: semantic chunking, vector store, semantic search

## Configuration Options

| Name | Data Type | Description | Default Value |
|------|-----------|-------------|---------------|
| buffer_size | `int` |  | `1` |
| breakpoint_percentile_threshold | `int` |  | `95` |
| top_k | `int` |  | `5` |

## Inputs

| Name | Data Type | Description |
|------|-----------|-------------|
| data | `Union[Chunks, list[Chunks]]` |  |
| id | `str` |  |
| query | `str` |  |
| run | `Any` |  |

## Outputs

| Name | Data Type | Description |
|------|-----------|-------------|
| info | `StoreInfoResponse` |  |
| data | `ParentType or GetDataError` |  |
| chunks | `list[FileChunk or WebDataChunk or GenericChunk]` |  |
| info | `StoreInfoResponse` |  |

## State Variables

| Name | Data Type | Description |
|------|-----------|-------------|
| chunks | `list[FileChunk or WebDataChunk or GenericChunk]` |  |
| chunk_embeddings | `list[list[float]]` |  |
| parents | `list[ParentType]` |  |
| last_info | `StoreInfoResponse` |  |



## Example(s)

## Error Handling

## FAQ

