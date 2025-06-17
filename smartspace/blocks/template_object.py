import json  # Proper import for JSON handling
from typing import Annotated, Any

from jinja2 import (
    BaseLoader,
    Environment,
    TemplateError,
)

from smartspace.core import Block, Config, Metadata, metadata, step
from smartspace.enums import BlockCategory, InputDisplayType


@metadata(
    category=BlockCategory.FUNCTION,
    description="Creates JSON objects from templates with dynamic variables. Renders Jinja2 template with input values and parses result as JSON. Use this for structured data generation.",
    icon="fa-code",
    label="template object, json template, dynamic object, structured data, generate json",
)
class TemplatedObject(Block):
    templated_json: Annotated[
        str,
        Config(),
        Metadata(
            display_type=InputDisplayType.TEMPLATEOBJECT,
            description="Jinja2 template with placeholders that renders to valid JSON.",
        ),
    ]

    @step(output_name="json")
    async def add_files(
        self,
        **inputs: Annotated[
            Any, Metadata(description="Variables to substitute in the template.")
        ],
    ) -> dict[str, Any]:
        try:
            # Use json.dumps for non-string types to ensure valid JSON formatting
            inputs = {
                key: f'"{value}"' if isinstance(value, str) else json.dumps(value)
                for key, value in inputs.items()
            }
            
            # Compile the Jinja2 template
            template = Environment(loader=BaseLoader()).from_string(self.templated_json)

            # Render the template with the provided inputs
            rendered_json = template.render(**inputs)

            # Parse the rendered template into a JSON object
            parsed_json = json.loads(rendered_json)

            # Send the parsed JSON as output
            return parsed_json
        except TemplateError as e:
            raise ValueError(f"Error in rendering Jinja2 template: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Error in parsing rendered template to JSON: {e}")
