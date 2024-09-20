from enum import Enum
from typing import Annotated, Any, Iterable

import httpx
from pydantic import BaseModel

from smartspace.core import Block, Config, Metadata, metadata, step
from smartspace.enums import BlockCategory


class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class RequestObject(BaseModel):
    method: HTTPMethod | None = None
    url: str = ""
    headers: dict[str, Any] = {}
    query_params: dict[str, Any] = {}
    body: dict[str, Any] | None = None


class ResponseObject(BaseModel):
    content: str | bytes | Iterable[bytes]
    headers: dict[Any, Any]
    body: Any
    status_code: int
    text: str


class HTTPError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response: ResponseObject | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


@metadata(
    description="Performs HTTP requests such as GET, POST, PUT, DELETE, and more.",
    category=BlockCategory.FUNCTION,
)
class HTTPRequest(Block):
    timeout: Annotated[int, Config()] = 30  # Timeout in seconds

    method: Annotated[HTTPMethod, Config()] = HTTPMethod.GET
    url: Annotated[str, Config()] = ""
    headers: Annotated[dict[str, Any] | None, Config()] = None
    query_params: Annotated[dict[str, Any] | None, Config()] = None
    body: Annotated[dict[str, Any] | None, Config()] = None

    @step(output_name="response")
    async def make_request(
        self,
        request: Annotated[
            RequestObject,
            Metadata(
                description="Can accept request parameters (method, url, headers, query_params, and/or body). Any values not specified will use the Config values. Pass an empty dict ({}) to use all Config values"
            ),
        ],
    ) -> ResponseObject:
        # Helper to get the effective value from request or config
        def get_effective_value(attr: str):
            return getattr(request, attr) or getattr(self, attr)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                url = get_effective_value("url")
                if not url:
                    raise ValueError("URL is required")
                response = await client.request(
                    method=get_effective_value("method"),
                    url=url,
                    headers=get_effective_value("headers") or {},
                    params=get_effective_value("query_params") or {},
                    json=get_effective_value("body")
                    if get_effective_value("method") in ["POST", "PUT", "PATCH"]
                    else None,
                )

                response.raise_for_status()

                content_type = response.headers.get("content-type", "")
                body = None
                if "application/json" in content_type:
                    try:
                        body = response.json()
                    except ValueError:
                        # JSON decoding failed, leave body as None
                        pass

                return ResponseObject(
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    text=response.text,
                    content=response.content,
                    body=body,
                )

            except httpx.RequestError as e:
                raise HTTPError(f"Network error occurred: {str(e)}")
            except httpx.HTTPStatusError as e:
                response_obj = ResponseObject(
                    status_code=e.response.status_code,
                    headers=dict(e.response.headers),
                    text=e.response.text,
                    content=e.response.content,
                    body=None,
                )
                raise HTTPError(
                    f"HTTP error occurred: {str(e)}",
                    e.response.status_code,
                    response_obj,
                )
            except Exception as e:
                raise HTTPError(f"Unexpected error occurred: {str(e)}")
