import json
from typing import Any

from smartspace.core import (
    Block,
    Output,
    metadata,
    step,
)

from app.api.models import ApiResponse, Source


@metadata(category={"name": "Misc"})
class CreateResponseWithSources(Block):
    response: Output[ApiResponse]

    @step()
    async def create_response(self, content: Any, sources: list[Source] | str | None):
        if not sources:
            sources = []

        # Check if sources is a string and convert to a list if necessary
        if isinstance(sources, str):
            sources = [Source(index=1, uri=sources)]

        # Emit the response
        self.response.send(
            ApiResponse(
                content=content
                if isinstance(content, str)
                else json.dumps(content, indent=4),
                sources=sources,
            )
        )
