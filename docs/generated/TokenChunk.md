# TokenChunk

## Overview


    Parse the document text into chunks with a fixed token size.

    Args:
    - chunk_size: The number of tokens to include in each chunk. (default is 200)
    - chunk_overlap: The number of tokens that overlap between consecutive
                        chunks. (default is 10)
    - separator: Default separator for splitting into words. (default is " ")

    This chunking method is particularly useful when:
    - You need precise control over the size of each chunk.
    - You're working with models that have specific token limits.
    - You want to ensure consistent chunk sizes across different types of text.

    Note: While this method provides consistent chunk sizes, it may split sentences
    or even words, which could affect the coherence of each chunk. Consider the
    trade-off between consistent size and semantic coherence when using this method.
    

!!! info "Details"

    === "Config"

        | Name | Data Type | Description | Default Value | Notes |
        |------|-----------|-------------|---------------|-------|
        | chunk_size | `int` | | | |
        | chunk_overlap | `int` | | | |
        | separator | `str` | | | |
        | model_name | `str` | | | |

    === "Inputs"

        | Name | Data Type | Description | Notes |
        |------|-----------|-------------|-------|
        | text | `str | list[str]` | | |

    === "Outputs"

        | Name | Data Type | Description | Notes |
        |------|-----------|-------------|-------|
        | result | `list[str]` | | |

## Example(s)

## Error Handling

## FAQ

## See Also
