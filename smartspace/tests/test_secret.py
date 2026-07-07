from typing import Annotated

from pydantic import TypeAdapter

from smartspace.core import Block, Config, Metadata, Secret, metadata, step
from smartspace.enums import BlockCategory
from smartspace.models import SecretRef


@metadata(description="test block with a secret config", category=BlockCategory.MISC)
class SecretConfigBlock(Block):
    api_key: Annotated[SecretRef, Config(), Secret()]
    plain: Annotated[str, Config()]
    documented_key: Annotated[
        SecretRef, Config(), Secret(), Metadata(display_name="API key")
    ]

    @step(output_name="out")
    async def run(self, x: str) -> str:
        return x


# ---------------------------------------------------------------------------
# Secret() marker — pin interface metadata
# ---------------------------------------------------------------------------

def test_secret_pin_metadata_has_secret_and_config():
    interface = SecretConfigBlock.interface()
    pin = interface.ports["api_key"].inputs[""]
    assert pin.metadata["secret"] is True
    assert pin.metadata["config"] is True


def test_plain_config_pin_has_no_secret_key():
    interface = SecretConfigBlock.interface()
    pin = interface.ports["plain"].inputs[""]
    assert "secret" not in pin.metadata
    assert pin.metadata["config"] is True


def test_secret_composes_with_metadata():
    interface = SecretConfigBlock.interface()
    pin = interface.ports["documented_key"].inputs[""]
    assert pin.metadata["secret"] is True
    assert pin.metadata["config"] is True
    assert pin.metadata["display_name"] == "API key"


def test_interface_serializes_with_secret_flag():
    interface = SecretConfigBlock.interface()
    dumped = interface.model_dump(by_alias=True)
    pin_metadata = dumped["ports"]["api_key"]["inputs"][""]["metadata"]
    assert pin_metadata["secret"] is True
    assert pin_metadata["config"] is True


# ---------------------------------------------------------------------------
# SecretRef — plain-string semantics
# ---------------------------------------------------------------------------

def test_secret_ref_validates_from_str():
    adapter = TypeAdapter(SecretRef)
    assert adapter.validate_python("my-secret-token") == "my-secret-token"


def test_secret_ref_serializes_as_plain_string():
    adapter = TypeAdapter(SecretRef)
    assert adapter.dump_python(SecretRef("my-secret-token")) == "my-secret-token"
    assert adapter.dump_json(SecretRef("my-secret-token")) == b'"my-secret-token"'


def test_secret_ref_json_schema_is_plain_string():
    adapter = TypeAdapter(SecretRef)
    assert adapter.json_schema() == {"type": "string"}


def test_secret_ref_pin_schema_is_plain_string():
    interface = SecretConfigBlock.interface()
    pin = interface.ports["api_key"].inputs[""]
    assert pin.json_schema == {"type": "string"}
