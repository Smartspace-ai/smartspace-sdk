# SemanticChunk

## Overview


    Semantic chunk parser.

    Splits a document into Chunks, with each node being a group of semantically related sentences.

    Args:
        buffer_size (int): number of sentences to group together when evaluating semantic similarity
        chunk_model: (BaseEmbedding): embedding model to use, defaults to BAAI/bge-small-en-v1.5
        breakpoint_percentile_threshold: (int): the percentile of cosine dissimilarity that must be exceeded between a group of sentences and the next to form a node. The smaller this number is, the more nodes will be generated
    

!!! info "Details"

    === "Config"

        | Name | Data Type | Description | Default Value | Notes |
        |------|-----------|-------------|---------------|-------|
        | buffer_size | `int` | | | |
        | breakpoint_percentile_threshold | `int` | | | |
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
