import json
from typing import Annotated, Any

from smartspace.core import Block, Config, Metadata, metadata, step
from smartspace.enums import BlockCategory, InputDisplayType
from smartspace.blocks._template_utils import (
    AutoJsonDict,
    AutoJsonList,
    AutoJsonScalar,
    AutoJsonWrapper,
    unwrap_for_json,
    wrap_auto_json,
)


@metadata(
    category=BlockCategory.TRANSFORM,
    description="""
    A block that takes a Jinja2 template string, fills the template,
    and then parses the result into a JSON object.
    """,
    icon="fa-code",
    label="template object, JSON templating, dynamic JSON, structured template, object generation",
    obsolete=True,
    deprecated_reason="Use the Transform block to extract and reshape data from JSON objects.",
    use_instead="Transform",
)
class TemplatedObject(Block):
    templated_json: Annotated[
        str,
        Config(),
        Metadata(
            display_type=InputDisplayType.TEMPLATEOBJECT,
            description="The Jinja2 template string that is formatted and parsed to JSON",
        ),
    ]

    @step(output_name="json")
    async def add_files(
        self,
        **inputs: Annotated[
            Any, Metadata(description="Objects passed to the Jinja2 template")
        ],
    ) -> dict[str, Any]:
        """
        Render the templated JSON from the Jinja2 template (self.templated_json),
        using the provided inputs, and then parse the result as JSON.
        """

        from jinja2 import BaseLoader, Environment, TemplateError

        try:
            env = Environment(loader=BaseLoader())
            template = env.from_string(self.templated_json)

            # Convert each input value into an AutoJson wrapper.
            # This allows dot-notation (e.g. person.sports) to become JSON automatically.
            wrapped_inputs = {k: wrap_auto_json(v) for k, v in inputs.items()}

            rendered_json = template.render(**wrapped_inputs)

            parsed_json = json.loads(rendered_json)
            return parsed_json

        except TemplateError as e:
            raise ValueError(f"Error in rendering Jinja2 template: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Error in parsing rendered template to JSON: {e}\n"
                f"Rendered output was:\n{rendered_json}"
            )


