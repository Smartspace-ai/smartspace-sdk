from typing import Annotated, Any

from smartspace.core import Block, BlockError, Config, Metadata, metadata, step
from smartspace.enums import BlockCategory
from smartspace.blocks._template_utils import make_jinja_env, wrap_auto_json


@metadata(
    category=BlockCategory.TRANSFORM,
    icon="fa-file-alt",
    label="template, jinja2, string template, render, format, interpolation",
    description=(
        "Renders a Jinja2 template string against named inputs. "
        "Use {{ name }} to reference connected inputs. "
        "A jmespath filter is available: {{ items | jmespath('[*].title') | join(', ') }}."
    ),
    obsolete=True,
    use_instead="StringTemplate",
)
class Template(Block):
    template: Annotated[
        str,
        Config(),
        Metadata(description="Jinja2 template string. Reference inputs with {{ name }}."),
    ]

    @step(output_name="string")
    async def render(
        self,
        **inputs: Annotated[Any, Metadata(description="Named inputs available in the template.")],
    ) -> str:
        env = make_jinja_env()
        wrapped = {k: wrap_auto_json(v) for k, v in inputs.items()}
        try:
            return env.from_string(self.template).render(**wrapped)
        except Exception as e:
            raise BlockError(f"Template rendering failed: {e}")
