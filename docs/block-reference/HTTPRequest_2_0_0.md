{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview

Asynchronous HTTP client with non-raising 4xx/5xx behavior. Supports `GET`, `POST`, `PUT`, `DELETE`, and `PATCH`, configurable headers and query params, and returns a structured `ResponseObject` with `status_code`, `headers`, `text`, `content`, and `body` (automatically parsed JSON when `content-type` indicates JSON, otherwise `text`).

## Description

Performs HTTP requests such as GET, POST, PUT, DELETE, and more.

Notes:
- Uses `httpx.AsyncClient` under the hood.
- Does not call `raise_for_status`; 4xx/5xx responses are returned as `ResponseObject` for the caller to inspect.
- If `content-type` is JSON, `body` contains the parsed JSON; otherwise `body` is set to the `text` response.
- `url` is required.

## Metadata

- **Category**: Function
- **Icon**: fa-cloud-download-alt
- **Label**: HTTP request, web API call, REST client, API request, web service call

## Configuration Options

| Name | Data Type | Description | Default Value |
|------|-----------|-------------|---------------|
| timeout | `int` | Request timeout (seconds) | `30` |
| method | `HTTPMethod` | One of `GET`, `POST`, `PUT`, `DELETE`, `PATCH` | `GET` |
| headers | `dict[str, Any]` | Headers applied to every request | `{}` |

## Inputs

| Name | Data Type | Description |
|------|-----------|-------------|
| url | `str` | Target URL (required) |
| body | `Any or None` | JSON-serializable body for `POST`/`PUT`/`PATCH`; ignored for others |
| query_params | `dict[str, Any] or None` | Query string parameters |

## Outputs

| Name | Data Type | Description |
|------|-----------|-------------|
| response | `ResponseObject` | Structured response with `status_code`, `headers`, `text`, `content`, and `body` (JSON when applicable) |

## State Variables

No state variables available.

{{ generate_block_details(page.title) }}


## Example(s)

### Example 1: GET JSON
- Config: `method=GET`, `headers={"Accept":"application/json"}`
- Call: `make_request(url="https://api.example.com/items")`
- Output: `response.body` is parsed JSON (list/dict); `status_code` e.g. `200`.

### Example 2: POST with JSON body
- Config: `method=POST`, `headers={"Content-Type":"application/json"}`
- Call: `make_request(url="https://api.example.com/items", body={"name":"foo"})`
- Output: `response.status_code` (e.g. `201`); `response.body` JSON when server returns JSON.

### Example 3: Non-JSON response
- Config: `method=GET`
- Call: `make_request(url="https://example.com/plain.txt")`
- Output: `response.body` equals `response.text`; `content` provides raw bytes.

### Example 4: Query parameters
- Call: `make_request(url="https://api.example.com/search", query_params={"q":"abc","page":2})`
- Output: `response.status_code`, `response.body` JSON or `text`.

## Error Handling
- If `url` is missing, raises `ValueError`.
- Network errors (DNS, connection, timeouts) propagate as `httpx` exceptions.
- 4xx/5xx are not raised; check `response.status_code` to detect error responses.

## FAQ

???+ question "Does it throw on 404 or 500?"

    No. It does not call `raise_for_status`, so `response.status_code` reflects 4xx/5xx and you can decide how to handle it.

???+ question "When does `body` contain parsed JSON?"

    When the response `content-type` indicates JSON (e.g. `application/json` or `text/json`). Otherwise `body` equals `text`.

???+ question "How do I send form data or files?"

    This version accepts JSON bodies via `body`. For forms/files, extend the block or issue a PR to add support for `data`/`files` arguments.
