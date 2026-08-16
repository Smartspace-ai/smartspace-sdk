import json
from pathlib import Path
from typing import Any

import pytest

from smartspace import schemas

SNAPSHOT = Path(__file__).parent / "snapshots" / "native_schemas.json"


def _snapshot() -> dict[str, dict[str, Any]]:
    return json.loads(SNAPSHOT.read_text(encoding="utf-8"))


def _registered() -> dict[str, dict[str, Any]]:
    return {
        f"{name}@{version}": interface.json_schema
        for name, versions in schemas.interfaces().items()
        for version, interface in versions.items()
    }


def test_published_schemas_are_unchanged():
    # A (name, version) is a contract flows pin to. If this fails you changed a
    # published shape: register a NEW version and add it to the snapshot instead
    # of editing the existing entry.
    assert _registered() == _snapshot()


def test_every_registered_schema_is_snapshotted():
    assert set(_registered()) == set(_snapshot())


def test_find_is_exact_match_only():
    assert schemas.find("File", "1.0.0") is not None
    assert schemas.find("File", "1") is None
    assert schemas.find("File", "^1.0.0") is None
    assert schemas.find("Nope", "1.0.0") is None


def test_register_same_version_same_shape_is_idempotent():
    from smartspace.models import File

    before = schemas.find("File", "1.0.0")
    assert schemas.register("File", "1.0.0", File) is before


def test_register_same_version_different_shape_raises():
    with pytest.raises(ValueError, match="immutable"):
        schemas.register("File", "1.0.0", str)


def test_serialises_schema_under_its_wire_name():
    payload = schemas.find("String", "1.0.0").model_dump(by_alias=True)
    assert payload == {
        "name": "String",
        "version": "1.0.0",
        "description": None,
        "schema": {"type": "string"},
    }
