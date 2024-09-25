{% set path = "assets/" + page.title + "-block.png" %}
{% if block_image_exists(path) %}
![{{page.title}}]({{path}}){{ block_image_sizing() }}
{% endif %}

## Overview
The `HTTPRequest` Block performs HTTP requests using methods such as GET, POST, PUT, DELETE, and PATCH. It supports passing request parameters, headers, query parameters, and request bodies. The Block outputs a `ResponseObject` containing the response content, headers, body, and status code.

By default, the request method is `GET`, but it can be configured using the available HTTP methods. If any values are not provided during the request, they will be fetched from the Block's configuration.

{{ generate_block_details(page.title) }}

## Example(s)

### Example 1: Perform a GET request
- Create an `HTTPRequest` Block.
- Set the `url` to `"https://api.example.com/data"`.
- Leave the method as `GET`.
- The Block will send a `GET` request to the provided URL and output the response, including the content, headers, and status code.

### Example 2: Perform a POST request with a JSON body
- Set up an `HTTPRequest` Block.
- Set the `method` to `POST`.
- Set the `url` to `"https://api.example.com/create"`.
- Provide a body such as `{"name": "John", "age": 30}`.
- The Block will send the `POST` request and return the response with the created data.

### Example 3: Handle request headers and query parameters
- Create an `HTTPRequest` Block.
- Set the `url` to `"https://api.example.com/data"`.
- Add headers like `{"Authorization": "Bearer token123"}`.
- Add query parameters such as `{"page": 1, "limit": 10}`.
- The Block will send a `GET` request with the headers and query parameters and return the response.

## Error Handling
- If the `URL` is missing, the Block will raise a `ValueError` indicating that the URL is required.
- Network-related errors will raise an `HTTPError` with a descriptive message, e.g., "Network error occurred".
- If the server responds with an HTTP error (status code 4xx or 5xx), an `HTTPError` will be raised with the corresponding `ResponseObject`.
- Any other unexpected exceptions will also raise an `HTTPError`.

## FAQ

???+ question "What happens if no method is provided?"
    
    If no method is provided in the request or configuration, the Block will default to the `GET` method for the request.

???+ question "Can I use this Block for asynchronous requests?"
    
    Yes, the `HTTPRequest` Block is designed for asynchronous requests. It uses the `httpx.AsyncClient` to handle the HTTP calls asynchronously.

???+ question "What happens if the response is not JSON?"
    
    If the response's content type is not `application/json`, the Block will still return the response content, but the `body` field in the `ResponseObject` will be `None`.

???+ question "How can I pass headers and query parameters dynamically?"
    
    Headers and query parameters can be passed either through the `RequestObject` when making the request or through the Block's configuration. Any values provided in the request will override the configuration values.