# SentenceChunk

## Overview


    Parse text with a preference for complete sentences.

    In general, this class tries to keep sentences and paragraphs together. Therefore
    compared to the original TokenTextSplitter, there are less likely to be
    hanging sentences or parts of sentences at the end of the node chunk.
    
    Args:
        chunk_size: The number of tokens to include in each chunk. (default is 200)
        chunk_overlap: The number of tokens that overlap between consecutive chunks. (default is 10)
        separator: Default separator for splitting into words. (default is " ")
        paragraph_separator: Separator between paragraphs. (default is "\n\n\n")
        secondary_chunking_regex: Backup regex for splitting into sentences.(default is "[^,\.;]+[,\.;]?".)
        
    Steps: 
        1: Break text into splits that are smaller than chunk size base on the separators and regex.
        2: Combine splits into chunks of size chunk_size (smaller than).

    

!!! info "Details"

    === "Config"

        | Name | Data Type | Description | Default Value | Notes |
        |------|-----------|-------------|---------------|-------|
        | chunk_size | `int` | | | |
        | chunk_overlap | `int` | | | |
        | separator | `str` | | | |
        | paragraph_separator | `str` | | | |
        | model_name | `str` | | | |
        | secondary_chunking_regex | `str` | | | |

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
