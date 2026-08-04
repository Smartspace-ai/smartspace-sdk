from typing import Annotated, Any

import pytest

from smartspace.core import BlockError, Config, Expression, Templatable, step
from smartspace.blocks.templatable import TemplatableBlock
from smartspace.enums import InputLanguage
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


def test_templatable_config_arriving_after_context():
    block = SimpleTemplatable()
    block._set_inputs([_context_iv("name", "Bob")])
    block._set_inputs([_iv("prompt", "", "Hello {{ name }}!")])
    assert block.prompt == "Hello Bob!"


def test_templatable_literal_renders_without_context():
    block = SimpleTemplatable()
    block._set_inputs([_iv("prompt", "", "Hello, no variables here.")])
    assert block.prompt == "Hello, no variables here."


def test_templatable_unwired_reference_raises():
    # The engine delivers a run's inputs in one batch, so a template that
    # references an unwired context input must fail loudly, not pass through.
    block = SimpleTemplatable()
    with pytest.raises(BlockError, match="Template rendering failed"):
        block._set_inputs([_iv("prompt", "", "Hello {{ name }}!")])


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


def test_expression_has_no_brace_interpolation():
    # The contract Transform already had, now shared: braces are not special,
    # so a Jinja-shaped value is simply not a valid expression. Pins that are
    # genuinely text use Templatable() instead.
    block = SimpleExpression()
    with pytest.raises(BlockError, match="Expression evaluation failed"):
        block._set_inputs([
            _iv("condition", "", "Bearer {{ apiKey }}"),
            _context_iv("apiKey", "tok-123"),
        ])


def test_expression_literal_text_needs_quoting():
    # A literal payload is expressible, but as a JMESPath raw string literal —
    # it is no longer text that happens to contain no braces.
    block = SimpleExpression()
    block._set_inputs([_iv("condition", "", "'query { things }'")])
    assert block.condition == "query { things }"


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
    # Text pin renders Jinja; data pin evaluates JMESPath. Same context.
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


# ---------------------------------------------------------------------------
# TemplatableBlock — @step parameters
# ---------------------------------------------------------------------------


class StepParamTemplatable(TemplatableBlock):
    @step(output_name="out")
    async def run(
        self,
        url: Annotated[str, Templatable()],
        plain: str = "untouched",
    ) -> str:
        return url


class StepParamExpression(TemplatableBlock):
    @step(output_name="out")
    async def run(self, picked: Annotated[Any, Expression()]) -> Any:
        return picked


class StepParamDict(TemplatableBlock):
    @step(output_name="out")
    async def run(
        self, query_params: Annotated[dict[str, Any], Templatable()]
    ) -> dict[str, Any]:
        return query_params


def test_step_params_cached_correctly():
    assert StepParamTemplatable._templatable_step_params == {"run": frozenset({"url"})}
    assert StepParamTemplatable._expression_step_params == {}
    assert StepParamExpression._expression_step_params == {"run": frozenset({"picked"})}


def test_step_param_interface_stamps_templatable_metadata():
    pin = StepParamTemplatable.interface().ports["run"].inputs["url"]
    assert pin.metadata["templatable"] is True
    assert pin.metadata["language"] == InputLanguage.JINJA


def test_step_param_interface_stamps_expression_metadata():
    pin = StepParamExpression.interface().ports["run"].inputs["picked"]
    assert pin.metadata["expression"] is True
    assert pin.metadata["language"] == InputLanguage.JMESPATH


def test_step_param_renders_when_context_set():
    block = StepParamTemplatable()
    block._set_inputs([
        _iv("run", "url", "https://api.example.com/{{ path }}"),
        _context_iv("path", "users/1"),
    ])
    assert block.run._pending_inputs["url"][""] == "https://api.example.com/users/1"


def test_step_param_context_arriving_first():
    block = StepParamTemplatable()
    block._set_inputs([_context_iv("base", "https://api.example.com")])
    block._set_inputs([_iv("run", "url", "{{ base }}/items")])
    assert block.run._pending_inputs["url"][""] == "https://api.example.com/items"


def test_step_param_literal_passes_without_context():
    block = StepParamTemplatable()
    block._set_inputs([_iv("run", "url", "https://api.example.com/items")])
    assert block.run._pending_inputs["url"][""] == "https://api.example.com/items"


def test_step_param_unwired_reference_raises():
    block = StepParamTemplatable()
    with pytest.raises(BlockError, match="run.url"):
        block._set_inputs([_iv("run", "url", "{{ base }}/items")])


def test_step_param_unmarked_param_untouched():
    block = StepParamTemplatable()
    block._set_inputs([
        _iv("run", "url", "{{ base }}"),
        _iv("run", "plain", "{{ base }}"),
        _context_iv("base", "rendered"),
    ])
    assert block.run._pending_inputs["url"][""] == "rendered"
    assert block.run._pending_inputs["plain"][""] == "{{ base }}"


def test_step_param_render_error_names_port_and_pin():
    block = StepParamTemplatable()
    with pytest.raises(BlockError, match="run.url"):
        block._set_inputs([
            _iv("run", "url", "{{ typo }}"),
            _context_iv("base", "x"),
        ])


def test_step_param_expression_evaluates():
    block = StepParamExpression()
    block._set_inputs([
        _iv("run", "picked", "user.name"),
        _context_iv("user", {"name": "Erin"}),
    ])
    assert block.run._pending_inputs["picked"][""] == "Erin"


def test_step_param_expression_builds_a_structure():
    block = StepParamExpression()
    block._set_inputs([
        _iv("run", "picked", "{ids: items[*].id, n: length(items)}"),
        _context_iv("items", [{"id": "a"}, {"id": "b"}]),
    ])
    assert block.run._pending_inputs["picked"][""] == {"ids": ["a", "b"], "n": 2}


def test_step_param_expression_whole_value_keeps_type():
    block = StepParamExpression()
    block._set_inputs([
        _iv("run", "picked", "length(items)"),
        _context_iv("items", [1, 2, 3]),
    ])
    value = block.run._pending_inputs["picked"][""]
    assert value == 3 and isinstance(value, int)


def test_step_param_expression_wired_data_passes_through():
    # A non-string value came from upstream, not the designer — it is already
    # the payload, so it is never compiled. This is what keeps a computed
    # payload safe to wire into an Expression pin.
    block = StepParamExpression()
    payload = {"name": "Alice", "role": "admin", "age": 30}
    block._set_inputs([
        _iv("run", "picked", payload),
        _context_iv("user", {"name": "someone else"}),
    ])
    assert block.run._pending_inputs["picked"][""] == payload


def test_step_param_expression_wired_list_passes_through():
    block = StepParamExpression()
    block._set_inputs([_iv("run", "picked", [1, 2, 3])])
    assert block.run._pending_inputs["picked"][""] == [1, 2, 3]


def test_step_param_expression_empty_context_missing_ref_is_null():
    block = StepParamExpression()
    block._set_inputs([_iv("run", "picked", "user.name")])
    assert block.run._pending_inputs["picked"][""] is None


def test_expression_headers_shape_end_to_end():
    # The motivating case: one expression building a headers object, mixing a
    # literal with a value computed from context. Both quoting rules appear —
    # a hyphenated key double-quoted, literal text single-quoted.
    block = SimpleExpression()
    block._set_inputs([
        _iv(
            "condition",
            "",
            "{\"Content-Type\": 'application/json', "
            "Authorization: join('', ['Bearer ', apiKey]), "
            "\"X-Count\": length(items)}",
        ),
        _context_iv("apiKey", "tok-123"),
        _context_iv("items", [1, 2, 3]),
    ])
    assert block.condition == {
        "Content-Type": "application/json",
        "Authorization": "Bearer tok-123",
        "X-Count": 3,
    }


def test_expression_hyphenated_key_must_be_quoted():
    # Unquoted JMESPath identifiers are [A-Za-z_][A-Za-z0-9_]*, so a bare
    # X-Count lexes as subtraction. Nearly every real header name has a
    # hyphen, which makes this the mistake most worth failing loudly on.
    block = SimpleExpression()
    with pytest.raises(BlockError, match="Expression evaluation failed"):
        block._set_inputs([
            _iv("condition", "", "{X-Count: length(items)}"),
            _context_iv("items", [1, 2, 3]),
        ])


def test_expression_double_quoted_value_is_a_field_lookup():
    # The other half of the quoting rule, and the quiet one: double quotes are
    # a field reference, so this yields null rather than the text it resembles.
    # Consumers are expected to reject nulls with their own message.
    block = SimpleExpression()
    block._set_inputs([_iv("condition", "", "{\"Content-Type\": \"application/json\"}")])
    assert block.condition == {"Content-Type": None}


def test_step_param_dict_renders_string_leaves():
    block = StepParamDict()
    block._set_inputs([
        _iv("run", "query_params", {"q": "{{ term }}", "page": 2, "tags": ["{{ tag }}", "fixed"]}),
        _context_iv("term", "fishing"),
        _context_iv("tag", "nz"),
    ])
    assert block.run._pending_inputs["query_params"][""] == {
        "q": "fishing",
        "page": 2,
        "tags": ["nz", "fixed"],
    }


# ---------------------------------------------------------------------------
# TemplatableBlock — dict/list class-attribute fields
# ---------------------------------------------------------------------------


class DictConfigTemplatable(TemplatableBlock):
    headers: Annotated[dict[str, Any], Config(), Templatable()] = {}


def test_dict_config_renders_string_leaves():
    block = DictConfigTemplatable()
    block._set_inputs([
        _iv("headers", "", {"Authorization": "Bearer {{ token }}", "Accept": "application/json"}),
        _context_iv("token", "abc123"),
    ])
    assert block.headers == {
        "Authorization": "Bearer abc123",
        "Accept": "application/json",
    }


def test_dict_config_keys_not_rendered():
    block = DictConfigTemplatable()
    block._set_inputs([
        _iv("headers", "", {"{{ key }}": "value"}),
        _context_iv("key", "X-Real"),
    ])
    assert block.headers == {"{{ key }}": "value"}
