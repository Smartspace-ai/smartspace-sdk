from typing import Annotated, Any

from jinja2 import BaseLoader, Environment

from smartspace.core import (
    Block,
    Config,
    metadata,
    step,
)
from smartspace.enums import BlockCategory


@metadata(
    description="Takes in a Jinja template string and renders it with the given inputs",
    category=BlockCategory.MISC,
)
class StringTemplate(Block):
    template: Annotated[str, Config()]

    @step(output_name="string")
    async def build(self, **inputs: Any) -> str:
        template = Environment(loader=BaseLoader()).from_string(self.template)
        return template.render(**inputs)
