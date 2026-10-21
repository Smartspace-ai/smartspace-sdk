import pytest

import smartspace.blocks.delay as delay_module
from smartspace.blocks.delay import Delay, Delay_1_1_0
from smartspace.core import Block, BlockSet
from smartspace.models import BlockPinRef, InputValue


@pytest.fixture
def sleeps(monkeypatch):
    calls: list[float] = []

    async def fake_sleep(seconds: float):
        calls.append(seconds)

    monkeypatch.setattr(delay_module.asyncio, "sleep", fake_sleep)
    return calls


async def _run(block: Block, inputs: dict[tuple[str, str], object]):
    block._load(
        inputs=[
            InputValue(target=BlockPinRef(port=port, pin=pin), value=value)
            for (port, pin), value in inputs.items()
        ]
    )
    call = await block._run_function("delay")
    messages = [m async for m in call]
    return [(o.source, o.value) for m in messages for o in m.outputs]


def _delay_ms_pin(block: type[Block]):
    return block.interface().ports["delay_ms"].inputs[""]


def test_delay_1_1_0_version():
    assert Delay_1_1_0.name == "Delay"
    assert Delay_1_1_0.version == "1.1.0"


def test_delay_1_1_0_delay_ms_is_required_without_default():
    pin = _delay_ms_pin(Delay_1_1_0)

    assert pin.required is True
    assert pin.default is None


def test_delay_1_0_0_delay_ms_keeps_default():
    pin = _delay_ms_pin(Delay)

    assert Delay.version == "1.0.0"
    assert pin.required is False
    assert pin.default == 1000


def test_delay_1_1_0_delay_ms_starts_dynamic():
    pin = _delay_ms_pin(Delay_1_1_0)

    assert not pin.metadata.get("config")
    assert pin.sticky is True


def test_delay_1_0_0_delay_ms_stays_fixed():
    pin = _delay_ms_pin(Delay)

    assert pin.metadata.get("config") is True
    assert pin.sticky is True


def test_delay_1_1_0_output_pins_match_1_0_0():
    def outputs(block: type[Block]):
        return {
            port_name: sorted(port.outputs)
            for port_name, port in block.interface().ports.items()
            if port.outputs
        }

    assert outputs(Delay_1_1_0) == outputs(Delay)


def test_both_versions_resolve_from_block_set():
    block_set = BlockSet()
    block_set.add(Delay)
    block_set.add(Delay_1_1_0)

    assert block_set.find("Delay", "1.0.0") is Delay
    assert block_set.find("Delay", "1.1.0") is Delay_1_1_0
    assert block_set.find("Delay", "1.0.X") is Delay


@pytest.mark.asyncio
async def test_delay_1_1_0_waits_delay_ms_and_forwards_data(sleeps):
    outputs = await _run(
        Delay_1_1_0(),
        {("delay_ms", ""): 10000, ("delay", "data"): {"status": "open"}},
    )

    assert sleeps == [10.0]
    assert outputs == [(BlockPinRef(port="output", pin=""), {"status": "open"})]


@pytest.mark.asyncio
async def test_delay_1_1_0_does_not_fall_back_to_a_default_wait(sleeps):
    with pytest.raises(TypeError):
        await _run(Delay_1_1_0(), {("delay", "data"): "x"})

    assert sleeps == []


@pytest.mark.asyncio
async def test_delay_1_0_0_waits_default_when_delay_ms_unset(sleeps):
    outputs = await _run(Delay(), {("delay", "data"): "x"})

    assert sleeps == [1.0]
    assert outputs == [(BlockPinRef(port="output", pin=""), "x")]
