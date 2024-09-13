# WindowChunk

## Overview


    Sentence window chunk parser.

    Splits a document into Chunks
    Each chunk contains a window from the surrounding sentences.

    Args:
        window_size: The number of sentences on each side of a sentence to capture.
    

!!! info "Details"

    === "Config"

        | Name | Data Type | Description | Default Value | Notes |
        |------|-----------|-------------|---------------|-------|
        | window_size | `int` | | | |

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
