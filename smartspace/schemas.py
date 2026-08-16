"""Native schema registry.

The platform-owned data shapes a flow input or output can name by
``(name, version)`` instead of pasting a JSON schema. A flow pin that says
``{"type": "Prompt", "typeVersion": "1.0.0"}`` resolves here — the same way a
block is resolved from its registry by ``name`` + ``version`` — so the pin
never carries a copy of the schema.

Shapes register from where they live: the SDK registers the models it owns
below; the AI API registers the ones it owns (``SourceList``) at import. The
endpoint serving them returns the union, exactly as ``/blocks`` does.

A published ``(name, version)`` is immutable. Change the shape → register a new
version. ``register`` enforces that: re-registering the same version with a
different schema raises.
"""

import json
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field

from smartspace.models import ContentItem, File
from smartspace.utils.utils import _get_type_adapter


class SchemaInterface(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    version: str
    description: str | None = None
    json_schema: Annotated[dict[str, Any], Field(alias="schema")]


_registry: dict[str, dict[str, SchemaInterface]] = {}


def register(
    name: str, version: str, annotation: Any, description: str | None = None
) -> SchemaInterface:
    schema = _get_type_adapter(annotation).json_schema()
    interface = SchemaInterface(
        name=name, version=version, description=description, json_schema=schema
    )

    existing = _registry.get(name, {}).get(version)
    if existing is not None:
        if _canonical(existing.json_schema) != _canonical(schema):
            raise ValueError(
                f"Schema {name}@{version} is already registered with a different "
                "shape. Published versions are immutable — register a new version."
            )
        return existing

    _registry.setdefault(name, {})[version] = interface
    return interface


def interfaces() -> dict[str, dict[str, SchemaInterface]]:
    return {name: dict(versions) for name, versions in _registry.items()}


def find(name: str, version: str) -> SchemaInterface | None:
    # Exact match only. Blocks resolve through an npm-style range spec; schemas
    # deliberately do not — a pin names one immutable shape.
    return _registry.get(name, {}).get(version)


def _canonical(schema: dict[str, Any]) -> str:
    return json.dumps(schema, sort_keys=True, separators=(",", ":"))


register(
    "Prompt",
    "1.0.0",
    list[ContentItem],
    "What a chat surface sends: text and inline images, in order.",
)
register("File", "1.0.0", File, "A stored file, by id and name.")
register("FileList", "1.0.0", list[File], "Attached files.")
register("String", "1.0.0", str)
register("Json", "1.0.0", Any, "Any JSON value.")
register(
    "Object",
    "1.0.0",
    dict[str, Any],
    "A JSON object of no declared shape — the escape hatch for one-off payloads.",
)
