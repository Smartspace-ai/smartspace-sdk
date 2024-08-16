from unittest.mock import Mock

import pytest

from smartspace.blocks.http import (
    HTTPError,
    HTTPMethod,
    HTTPRequest,
    RequestObject,
)


@pytest.fixture(scope="function")
def mock_block():
    return Mock(
        spec=HTTPRequest,
        timeout=30,
        response_handling="json",
        method=HTTPMethod.GET,
        url="",
        headers={},
        body={},
        query_params={},
        response=Mock(),
        status_code=Mock(),
        response_headers=Mock(),
        error=Mock(),
    )


@pytest.mark.asyncio
async def test_make_request_get(mock_block: Mock):
    http_r = HTTPRequest(Mock(), Mock())

    request_object = RequestObject(
        method=HTTPMethod.GET,
        url="https://api.github.com/users/octocat",
    )

    response = await http_r.make_request._fn(mock_block, request_object)
    assert response.status_code == 200  # 200 OK


@pytest.mark.asyncio
async def test_make_request_error(mock_block: Mock):
    http_r = HTTPRequest(Mock(), Mock())

    request_object = RequestObject(
        method=HTTPMethod.GET,
        url="https://dummyjson.com/http/404/Hello_Peter",
    )

    with pytest.raises(HTTPError):
        await http_r.make_request._fn(mock_block, request_object)


@pytest.mark.asyncio
async def test_make_request_post(mock_block: Mock):
    request_object = RequestObject(
        method=HTTPMethod.POST,
        url="https://jsonplaceholder.typicode.com/posts",
        headers={"Content-Type": "application/json"},
        body={"title": "foo", "body": "bar", "userId": 1},
    )

    response = await HTTPRequest.make_request._fn(mock_block, request_object)
    assert response.status_code == 201  # 201 Created
    assert response.body["id"]  # Check if 'id' key is in the response


@pytest.mark.asyncio
async def test_make_request_put(mock_block: Mock):
    request_object = RequestObject(
        method=HTTPMethod.PUT,
        url="https://jsonplaceholder.typicode.com/posts/1",
        headers={"Content-Type": "application/json"},
        body={"id": 1, "title": "foo", "body": "bar", "userId": 1},
    )

    response = await HTTPRequest.make_request._fn(mock_block, request_object)

    assert response.status_code == 200  # 200 OK
    assert response.body["title"]  # Check if 'title' key is in the response


@pytest.mark.asyncio
async def test_make_request_delete(mock_block: Mock):
    request_object = RequestObject(
        method=HTTPMethod.DELETE,
        url="https://jsonplaceholder.typicode.com/posts/1",
    )

    response = await HTTPRequest.make_request._fn(mock_block, request_object)

    assert response.status_code == 200  # 200 OK, indicating the resource was deleted
    assert response.body == {}  # Response body should be empty on successful deletion


@pytest.mark.asyncio
async def test_make_request_get_with_query_params(mock_block: Mock):
    request_object = RequestObject(
        method=HTTPMethod.GET,
        url="https://jsonplaceholder.typicode.com/comments",
        query_params={"postId": 1},
    )

    response = await HTTPRequest.make_request._fn(mock_block, request_object)

    assert response.status_code == 200  # 200 OK
    assert (
        response.body[0]["postId"] == 1
    )  # Ensure the query parameter is reflected in the response
