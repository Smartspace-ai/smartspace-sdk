import json
from typing import Annotated, Any

from smartspace.core import Block, Config, Metadata, metadata, step
from smartspace.enums import BlockCategory, InputDisplayType


@metadata(
    category=BlockCategory.FUNCTION,
    description="""
    A block that takes a Jinja2 template string, fills the template,
    and then parses the result into a JSON object.
    """,
    icon="fa-code",
    label="template object, JSON templating, dynamic JSON, structured template, object generation",
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


class AutoJsonWrapper:
    """
    Base class that ensures that when converted to a string,
    we produce valid JSON of the wrapped data.
    """

    def __init__(self, data):
        self._data = data

    def __str__(self):
        from markupsafe import Markup

        # When Jinja calls str(...) on this object, we dump it as JSON
        # and mark it safe so it doesn't get escaped again.
        return Markup(json.dumps(self._unwrap()))

    def _unwrap(self):
        # By default, just return the underlying data.
        # Subclasses can override if needed.
        return self._data


class AutoJsonDict(AutoJsonWrapper):
    """
    Wraps a dict so that attribute or item lookups return more wrappers.
    """

    def __getitem__(self, key):
        return wrap_auto_json(self._data[key])

    def __getattr__(self, key):
        # If we do person.sports, Jinja calls __getattr__('sports')
        return self.__getitem__(key)

    def _unwrap(self):
        # Recursively produce a normal dict for final json.dumps
        return {k: unwrap_for_json(v) for k, v in self._data.items()}


class AutoJsonList(AutoJsonWrapper):
    """
    Wraps a list so that item lookups return more wrappers.
    """

    def __getitem__(self, idx):
        return wrap_auto_json(self._data[idx])

    def __len__(self):
        return len(self._data)

    def _unwrap(self):
        return [unwrap_for_json(item) for item in self._data]


class AutoJsonScalar(AutoJsonWrapper):
    """
    Wraps a scalar (string, int, float, bool, None)
    """

    # In most cases, the base class behavior is enough.
    # We just define it for clarity.


def wrap_auto_json(value):
    """
    Return an AutoJson wrapper appropriate for the given value.
    """
    if isinstance(value, dict):
        return AutoJsonDict(value)
    elif isinstance(value, list):
        return AutoJsonList(value)
    else:
        # String, int, float, bool, or any other scalar
        return AutoJsonScalar(value)


def unwrap_for_json(wrapper):
    """
    If 'wrapper' is an AutoJsonWrapper, recursively convert it to
    normal Python objects for final JSON serialization. Otherwise
    just return it.
    """
    if isinstance(wrapper, AutoJsonDict):
        return {k: unwrap_for_json(v) for k, v in wrapper._data.items()}
    elif isinstance(wrapper, AutoJsonList):
        return [unwrap_for_json(item) for item in wrapper._data]
    elif isinstance(wrapper, AutoJsonScalar):
        return wrapper._data
    else:
        return wrapper
