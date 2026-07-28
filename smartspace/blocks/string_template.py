from typing import Annotated, Any

from smartspace.core import (
    Block,
    BlockError,
    Config,
    Metadata,
    metadata,
    step,
)
from smartspace.enums import BlockCategory, InputLanguage


@metadata(
    description="Takes in a Jinja template string and renders it with the given inputs",
    category=BlockCategory.TRANSFORM,
    icon="fa-file-alt",
    label="string template, text formatting, variable substitution, format string, template interpolation",
)
class StringTemplate(Block):
    template: Annotated[str, Config(), Metadata(language=InputLanguage.JINJA)]

    @step(output_name="string")
    async def build(self, **inputs: Any) -> str:
        from jinja2 import BaseLoader, Environment

        template = Environment(loader=BaseLoader()).from_string(self.template)
        return template.render(**inputs)


@metadata(
    description=(
        "Renders a Jinja2 template string against named inputs. "
        "Use {{ name }} to reference connected inputs. "
        "A jmespath filter is available: {{ items | jmespath('[*].title') | join(', ') }}. "
        "Complex objects are serialised automatically."
    ),
    category=BlockCategory.TRANSFORM,
    icon="fa-file-alt",
    label="string template, text formatting, variable substitution, format string, template interpolation, jinja2, render",
)
class StringTemplate_2_0_0(Block):
    template: Annotated[str, Config(), Metadata(language=InputLanguage.JINJA)]

    @step(output_name="string")
    async def build(self, **inputs: Any) -> str:
        from smartspace.blocks._template_utils import make_jinja_env, wrap_auto_json

        env = make_jinja_env()
        wrapped = {k: wrap_auto_json(v) for k, v in inputs.items()}
        try:
            return env.from_string(self.template).render(**wrapped)
        except Exception as e:
            raise BlockError(f"Template rendering failed: {e}")
