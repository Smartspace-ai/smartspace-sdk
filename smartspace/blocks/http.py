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
    icon="fa-cloud-download-alt",
    label="HTTP request, web API call, REST client, API request, web service call",
)
class HTTPRequest(Block):
    timeout: Annotated[int, Config()] = 30  # Timeout in seconds
    method: Annotated[HTTPMethod, Config()] = HTTPMethod.GET
    headers: Annotated[dict[str, Any] , Config()] = {}

    @step(output_name="response")
    async def make_request(
        self,
        url: Annotated[str, Metadata(description="The URL to send the request to")],
        query_params: Annotated[dict[str, Any] , Metadata(description="Query parameters to include in the URL")] = {},
        body: Annotated[dict[str, Any], Metadata(description="Request body for POST, PUT, or PATCH requests")] = {},
    ) -> ResponseObject:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                if not url:
                    raise ValueError("URL is required")
                
                response = await client.request(
                    method=self.method,
                    url=url,
                    headers=self.headers ,
                    params=query_params ,
                    json=body if self.method in ["POST", "PUT", "PATCH"] else None,
                )

                response.raise_for_status()

                content_type = response.headers.get("content-type", "")
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
