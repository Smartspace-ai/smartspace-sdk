import pytest

from smartspace.blocks.template import Template
from smartspace.core import BlockError


async def _render(template_str: str, **inputs):
    block = Template()
    block.template = template_str
    return await block.render(**inputs)


# ---------------------------------------------------------------------------
# Template block
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_basic_substitution():
    result = await _render("Hello {{ name }}!", name="World")
    assert result == "Hello World!"


@pytest.mark.asyncio
async def test_multiple_inputs():
    result = await _render("{{ a }} + {{ b }}", a="foo", b="bar")
    assert result == "foo + bar"


@pytest.mark.asyncio
async def test_jmespath_filter():
    result = await _render(
        "{{ items | jmespath('[*].name') | join(', ') }}",
        items=[{"name": "Alice"}, {"name": "Bob"}],
    )
    assert result == "Alice, Bob"


@pytest.mark.asyncio
async def test_autojson_dot_access():
    result = await _render("{{ user.name }}", user={"name": "Charlie"})
    assert result == "Charlie"


@pytest.mark.asyncio
async def test_object_serialises_to_json():
    result = await _render("{{ obj }}", obj={"x": 1})
    assert result == '{"x": 1}'


@pytest.mark.asyncio
async def test_trim_blocks():
    result = await _render(
        "start\n{% if flag %}\nyes\n{% endif %}\nend",
        flag=True,
    )
    assert result == "start\nyes\nend"


@pytest.mark.asyncio
async def test_strict_undefined_raises():
    with pytest.raises(BlockError, match="Template rendering failed"):
        await _render("{{ missing_var }}")
