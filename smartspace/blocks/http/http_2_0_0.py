from enum import Enum
from typing import Annotated, Any, Optional

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
    content: bytes
    headers: dict[Any, Any]
    body: Any
    status_code: int
    text: str


@metadata(
    description="Performs HTTP requests such as GET, POST, PUT, DELETE, and more.",
    category=BlockCategory.FUNCTION,
    icon="fa-cloud-download-alt",
    label="HTTP request, web API call, REST client, API request, web service call",
)
class HTTPRequest_2_0_0(Block):
    timeout: Annotated[int, Config()] = 30  # Timeout in seconds

    method: Annotated[HTTPMethod, Config()] = HTTPMethod.GET
    headers: Annotated[
        dict[str, Any], Config()
    ] = {}  # NOTE: mutable default is fine if your framework handles it

    @step(output_name="response")
    async def make_request(
        self,
        url: Annotated[str, Metadata(description="The URL to send the request to")],
        body: Annotated[
            Optional[Any],
            Metadata(
                description="Request body for POST, PUT, or PATCH requests. Can be a dict, list, or raw JSON-compatible value."
            ),
        ] = None,
        query_params: Annotated[
            Optional[dict[str, Any]], Metadata(description="Query parameters")
        ] = None,
    ) -> ResponseObject:
        if not url:
            raise ValueError("URL is required")

        query_params = query_params or {}
        json_body = (
            body
            if self.method in {HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.PATCH}
            else None
        )

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=self.method.value,  # ensure str
                url=url,
                headers=self.headers,
                params=query_params,
                json=json_body,
            )

            content_type = response.headers.get("content-type", "").lower()
            response_body = (
                response.json()
                if "application/json" in content_type or "text/json" in content_type
                else response.text
            )

            return ResponseObject(
                status_code=response.status_code,
                headers=dict(response.headers.items()),
                text=response.text,
                content=response.content,
                body=response_body,
            )
