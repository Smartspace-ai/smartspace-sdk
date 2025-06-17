from typing import Annotated, Any

from jinja2 import BaseLoader, Environment

from smartspace.core import (
    Block,
    Config,
    Metadata,
    metadata,
    step,
)
from smartspace.enums import BlockCategory


@metadata(
    description="Renders text templates with dynamic variables. Configure a template with placeholders and fill them with input values. Use this for dynamic text generation.",
    category=BlockCategory.MISC,
    icon="fa-file-alt",
    label="template, text formatting, variable substitution, dynamic text, render",
)
class StringTemplate(Block):
    template: Annotated[str, Config(), Metadata(description="Jinja2 template with placeholders.")]

    @step(output_name="string")
    async def build(self, **inputs: Any) -> str:
        template = Environment(loader=BaseLoader()).from_string(self.template)
        return template.render(**inputs)
