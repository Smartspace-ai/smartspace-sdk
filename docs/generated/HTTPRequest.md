# HTTPRequest

## Overview

Performs HTTP requests such as GET, POST, PUT, DELETE, and more.

!!! info "Details"

    === "Config"

        | Name | Data Type | Description | Default Value | Notes |
        |------|-----------|-------------|---------------|-------|
        | timeout | `int` | | | |
        | method | `HTTPMethod` | | | |
        | url | `str` | | | |
        | headers | `dict[Tuple[str, Any]] | None` | | | |
        | query_params | `dict[Tuple[str, Any]] | None` | | | |
        | body | `dict[Tuple[str, Any]] | None` | | | |

    === "Inputs"

        | Name | Data Type | Description | Notes |
        |------|-----------|-------------|-------|
        | request | `Annotated[Tuple[RequestObject, Any]]` | | |

    === "Outputs"

        | Name | Data Type | Description | Notes |
        |------|-----------|-------------|-------|
        | response | `ResponseObject` | | |

## Example(s)

## Error Handling

## FAQ

## See Also
