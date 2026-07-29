from typing import Annotated

from smartspace.blocks.string_template import StringTemplate, StringTemplate_2_0_0
from smartspace.blocks.transform import Transform
from smartspace.core import (
    Block,
    Config,
    Expression,
    Metadata,
    Templatable,
    metadata,
    step,
)
from smartspace.enums import BlockCategory, InputLanguage


@metadata(description="test block with language-bearing configs", category=BlockCategory.MISC)
class LanguageConfigBlock(Block):
    templated: Annotated[str, Config(), Templatable()]
    expression: Annotated[str, Config(), Expression()]
    plain: Annotated[str, Config()]
    # An explicit language must win over the marker's default.
    overridden: Annotated[
        str, Config(), Templatable(), Metadata(language=InputLanguage.JMESPATH)
    ]

    @step(output_name="out")
    async def run(self, x: str) -> str:
        return x


def _pin(block: type[Block], name: str):
    return block.interface().ports[name].inputs[""]


# ---------------------------------------------------------------------------
# Markers stamp the language automatically
# ---------------------------------------------------------------------------


def test_templatable_pin_is_tagged_jinja():
    pin = _pin(LanguageConfigBlock, "templated")
    assert pin.metadata["templatable"] is True
    assert pin.metadata["language"] == InputLanguage.JINJA


def test_expression_pin_is_tagged_jmespath():
    pin = _pin(LanguageConfigBlock, "expression")
    assert pin.metadata["expression"] is True
    assert pin.metadata["language"] == InputLanguage.JMESPATH


def test_plain_config_pin_has_no_language():
    pin = _pin(LanguageConfigBlock, "plain")
    assert "language" not in pin.metadata
    assert pin.metadata["config"] is True


def test_explicit_language_beats_marker_default():
    pin = _pin(LanguageConfigBlock, "overridden")
    assert pin.metadata["templatable"] is True
    assert pin.metadata["language"] == InputLanguage.JMESPATH


# ---------------------------------------------------------------------------
# Real blocks carry the tag the flow designer keys off
# ---------------------------------------------------------------------------


def test_transform_expression_is_jmespath():
    assert _pin(Transform, "expression").metadata["language"] == InputLanguage.JMESPATH


def test_string_template_is_jinja():
    assert _pin(StringTemplate, "template").metadata["language"] == InputLanguage.JINJA
    assert (
        _pin(StringTemplate_2_0_0, "template").metadata["language"]
        == InputLanguage.JINJA
    )


# ---------------------------------------------------------------------------
# The value that crosses the wire is the plain string the designer compares to
# ---------------------------------------------------------------------------


def test_language_serialises_to_its_string_value():
    dumped = Transform.interface().model_dump(mode="json")
    assert dumped["ports"]["expression"]["inputs"][""]["metadata"]["language"] == "jmespath"


def test_get_path_is_jsonpath():
    from smartspace.blocks.json_blocks import Get

    pin = _pin(Get, "path")
    assert pin.metadata["language"] == InputLanguage.JSONPATH


def test_sql_condition_and_regex_pins_are_tagged():
    from smartspace.blocks.conditionals import Filter, If
    from smartspace.blocks.regex_match import RegexMatch
    from smartspace.blocks.sql import SQL

    assert _pin(SQL, "query").metadata["language"] == InputLanguage.SQL
    assert _pin(If, "condition").metadata["language"] == InputLanguage.CONDITION
    assert _pin(Filter, "condition").metadata["language"] == InputLanguage.CONDITION
    assert _pin(RegexMatch, "regex").metadata["language"] == InputLanguage.REGEX


def test_condition_pins_carry_the_expression_guide():
    from smartspace.blocks.conditionals import If
    from smartspace.utils.expressions import expression_tooltip

    assert _pin(If, "condition").metadata["description"] == expression_tooltip
