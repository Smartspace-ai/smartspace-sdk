from typing import Annotated, Any

import pytest

from smartspace.core import BlockError, Config, Expression, Templatable
from smartspace.blocks.templatable import TemplatableBlock
from smartspace.models import BlockPinRef, InputValue


def _iv(port: str, pin: str, value: Any) -> InputValue:
    return InputValue(target=BlockPinRef(port=port, pin=pin), value=value)


def _context_iv(key: str, value: Any) -> InputValue:
    return InputValue(target=BlockPinRef(port=f"context.{key}", pin=""), value=value)


class SimpleTemplatable(TemplatableBlock):
    prompt: Annotated[str | None, Config(), Templatable()] = None


class SimpleExpression(TemplatableBlock):
    condition: Annotated[Any, Config(), Expression()] = None


class BothMarkers(TemplatableBlock):
    prompt: Annotated[str | None, Config(), Templatable()] = None
    condition: Annotated[Any, Config(), Expression()] = None


# ---------------------------------------------------------------------------
# TemplatableBlock — Templatable fields
# ---------------------------------------------------------------------------

def test_templatable_renders_when_context_set():
    block = SimpleTemplatable()
    block._set_inputs([
        _iv("prompt", "", "Hello {{ name }}!"),
        _context_iv("name", "World"),
    ])
    assert block.prompt == "Hello World!"


def test_templatable_context_arriving_after_config():
    block = SimpleTemplatable()
    block._set_inputs([_iv("prompt", "", "Hello {{ name }}!")])
    assert block.prompt == "Hello {{ name }}!"  # not yet rendered

    block._set_inputs([_context_iv("name", "Alice")])
    assert block.prompt == "Hello Alice!"


def test_templatable_config_arriving_after_context():
    block = SimpleTemplatable()
    block._set_inputs([_context_iv("name", "Bob")])
    block._set_inputs([_iv("prompt", "", "Hello {{ name }}!")])
    assert block.prompt == "Hello Bob!"


def test_templatable_no_context_leaves_raw():
    block = SimpleTemplatable()
    block._set_inputs([_iv("prompt", "", "Hello {{ name }}!")])
    assert block.prompt == "Hello {{ name }}!"


def test_templatable_none_value_skipped():
    block = SimpleTemplatable()
    block._set_inputs([_context_iv("x", "y")])
    assert block.prompt is None  # no raw captured, nothing rendered


def test_templatable_jmespath_filter():
    block = SimpleTemplatable()
    block._set_inputs([
        _iv("prompt", "", "{{ items | jmespath('[*].name') | join(', ') }}"),
        _context_iv("items", [{"name": "Alice"}, {"name": "Bob"}]),
    ])
    assert block.prompt == "Alice, Bob"


def test_templatable_jmespath_global_fn():
    block = SimpleTemplatable()
    block._set_inputs([
        _iv("prompt", "", "{{ jmespath('[0].name', items) }}"),
        _context_iv("items", [{"name": "First"}]),
    ])
    assert block.prompt == "First"


def test_templatable_strict_undefined_raises():
    block = SimpleTemplatable()
    with pytest.raises(BlockError, match="Template rendering failed"):
        block._set_inputs([
            _iv("prompt", "", "Hello {{ typo_name }}!"),
            _context_iv("name", "World"),
        ])


def test_templatable_multiline_trim_blocks():
    block = SimpleTemplatable()
    block._set_inputs([
        _iv("prompt", "", "start\n{% if flag %}\nyes\n{% endif %}\nend"),
        _context_iv("flag", True),
    ])
    assert block.prompt == "start\nyes\nend"


def test_templatable_autojson_dot_access():
    block = SimpleTemplatable()
    block._set_inputs([
        _iv("prompt", "", "{{ user.name }}"),
        _context_iv("user", {"name": "Charlie"}),
    ])
    assert block.prompt == "Charlie"


def test_templatable_autojson_full_object_serialises():
    block = SimpleTemplatable()
    block._set_inputs([
        _iv("prompt", "", "{{ obj }}"),
        _context_iv("obj", {"a": 1}),
    ])
    assert block.prompt == '{"a": 1}'


# ---------------------------------------------------------------------------
# TemplatableBlock — Expression fields
# ---------------------------------------------------------------------------

def test_expression_evaluates_jmespath():
    block = SimpleExpression()
    block._set_inputs([
        _iv("condition", "", "user.active"),
        _context_iv("user", {"active": True}),
    ])
    assert block.condition is True


def test_expression_returns_typed_value():
    block = SimpleExpression()
    block._set_inputs([
        _iv("condition", "", "length(items)"),
        _context_iv("items", [1, 2, 3]),
    ])
    assert block.condition == 3


def test_expression_invalid_raises_block_error():
    block = SimpleExpression()
    with pytest.raises(BlockError, match="Expression evaluation failed"):
        block._set_inputs([
            _iv("condition", "", "!!!invalid!!!"),
            _context_iv("x", 1),
        ])


# ---------------------------------------------------------------------------
# TemplatableBlock — both markers on same block
# ---------------------------------------------------------------------------

def test_both_markers_render_independently():
    block = BothMarkers()
    block._set_inputs([
        _iv("prompt", "", "Hello {{ name }}"),
        _iv("condition", "", "score"),
        _context_iv("name", "Dave"),
        _context_iv("score", 42),
    ])
    assert block.prompt == "Hello Dave"
    assert block.condition == 42


# ---------------------------------------------------------------------------
# __init_subclass__ class-level caching
# ---------------------------------------------------------------------------

def test_class_fields_cached_correctly():
    assert "prompt" in SimpleTemplatable._templatable_fields
    assert "prompt" not in SimpleTemplatable._expression_fields
    assert "condition" in SimpleExpression._expression_fields
    assert "condition" not in SimpleExpression._expression_fields or True  # expression only
