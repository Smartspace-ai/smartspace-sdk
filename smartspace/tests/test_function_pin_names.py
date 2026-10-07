from typing import Annotated

import pytest

from smartspace.core import Block, Config, Output, Tool, callback, step
from smartspace.models import BlockPinRef, InputValue


async def _run(block: Block, function_name: str, inputs: dict[str, object]):
    block._load(
        inputs=[
            InputValue(target=BlockPinRef(port=function_name, pin=pin), value=value)
            for pin, value in inputs.items()
        ]
    )
    call = await block._run_function(function_name)
    messages = [m async for m in call]
    return call.result, messages


class NamePinStepBlock(Block):
    @step()
    async def echo(self, name: str) -> str:
        return name


@pytest.mark.asyncio
async def test_step_pin_named_name_keeps_step_name():
    block = NamePinStepBlock()

    result, messages = await _run(block, "echo", {"name": "hello"})

    assert result == "hello"
    assert block.echo.name == "echo"
    assert messages[0].outputs[0].source == BlockPinRef(port="echo", pin="")
    assert messages[0].outputs[0].value == "hello"


@pytest.mark.asyncio
async def test_step_pin_named_name_direct_call():
    block = NamePinStepBlock()

    result = await block.echo("hello")

    assert result == "hello"
    assert block.get_messages()[0].outputs[0].source == BlockPinRef(port="echo", pin="")


class OutputNamePinStepBlock(Block):
    @step(output_name="result")
    async def echo(self, _output_name: str) -> str:
        return _output_name


class PendingInputsPinStepBlock(Block):
    @step()
    async def echo(self, _pending_inputs: str) -> str:
        return _pending_inputs


class FnPinStepBlock(Block):
    @step()
    async def echo(self, _fn: str) -> str:
        return _fn


class BlockPinStepBlock(Block):
    @step()
    async def echo(self, _block: str) -> str:
        return _block


class MetadataPinStepBlock(Block):
    @step()
    async def echo(self, metadata: str) -> str:
        return metadata


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "block_type,pin_name",
    [
        (OutputNamePinStepBlock, "_output_name"),
        (PendingInputsPinStepBlock, "_pending_inputs"),
        (FnPinStepBlock, "_fn"),
        (BlockPinStepBlock, "_block"),
        (MetadataPinStepBlock, "metadata"),
    ],
)
async def test_step_pin_named_after_function_attribute(
    block_type: type[Block], pin_name: str
):
    block = block_type()

    result, _ = await _run(block, "echo", {pin_name: "hello"})

    assert result == "hello"
    assert block.echo.name == "echo"
    assert isinstance(block.echo.metadata, dict)


@pytest.mark.asyncio
async def test_step_pin_named_output_name_keeps_output_label():
    block = OutputNamePinStepBlock()

    _, messages = await _run(block, "echo", {"_output_name": "hello"})

    assert messages[0].outputs[0].source == BlockPinRef(port="echo", pin="result")


class NameOutputStepBlock(Block):
    @step(output_name="name")
    async def echo(self, value: str) -> str:
        return value


@pytest.mark.asyncio
async def test_step_output_named_name_keeps_step_name():
    block = NameOutputStepBlock()

    result, messages = await _run(block, "echo", {"value": "hello"})

    assert result == "hello"
    assert block.echo.name == "echo"
    assert messages[0].outputs[0].source == BlockPinRef(port="echo", pin="name")


class PendingInputsOutputStepBlock(Block):
    @step(output_name="_pending_inputs")
    async def echo(self, value: str) -> str:
        return value


@pytest.mark.asyncio
async def test_step_output_named_pending_inputs_receives_input():
    block = PendingInputsOutputStepBlock()

    result, _ = await _run(block, "echo", {"value": "hello"})

    assert result == "hello"


class NoInputStepBlock(Block):
    @step()
    async def run(self) -> int:
        return 1


@pytest.mark.asyncio
async def test_step_without_inputs_or_output_name_runs():
    block = NoInputStepBlock()

    result, messages = await _run(block, "run", {})

    assert result == 1
    assert messages[0].outputs[0].source == BlockPinRef(port="run", pin="")


# Same shape as the native guid_generator_v5 and sentence_chunk blocks: a `name`
# input, no return annotation, output sent through a block-level Output
class NamePinSendStepBlock(Block):
    guid: Output[str]

    @step()
    async def generate(self, name: str):
        self.guid.send(f"id-{name}")


class DefaultNamePinSendStepBlock(Block):
    guid: Output[str]

    @step()
    async def generate(self, name: str = ""):
        self.guid.send(f"id-{name}")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "block_type", [NamePinSendStepBlock, DefaultNamePinSendStepBlock]
)
async def test_step_pin_named_name_without_return_emits_block_output(
    block_type: type[Block],
):
    block = block_type()

    _, messages = await _run(block, "generate", {"name": "hello"})

    outputs = [output for message in messages for output in message.outputs]
    assert [(output.source, output.value) for output in outputs] == [
        (BlockPinRef(port="guid", pin=""), "id-hello")
    ]


class NamePinCallbackBlock(Block):
    received: list[str] = []

    @callback()
    async def on_result(self, name: str):
        self.received.append(name)


@pytest.mark.asyncio
async def test_callback_pin_named_name_keeps_callback_name():
    block = NamePinCallbackBlock()
    block.received = []

    await _run(block, "on_result", {"name": "hello"})

    assert block.received == ["hello"]
    assert block.on_result.name == "on_result"


class PendingInputsPinCallbackBlock(Block):
    received: list[str] = []

    @callback()
    async def on_result(self, _pending_inputs: str):
        self.received.append(_pending_inputs)


@pytest.mark.asyncio
async def test_callback_pin_named_pending_inputs_receives_input():
    block = PendingInputsPinCallbackBlock()
    block.received = []

    await _run(block, "on_result", {"_pending_inputs": "hello"})

    assert block.received == ["hello"]


class ConfiguredTool(Tool):
    description: Annotated[str, Config()]

    def run(self, a: int) -> int: ...


class ToolBlock(Block):
    tool: ConfiguredTool

    @step()
    async def run(self, a: int) -> int:
        return a


def test_tool_config_pin_without_default_is_seeded():
    block = ToolBlock()

    assert block.tool.description is None


class Settings:
    value: Annotated[int, Config()]


class SettingsPortBlock(Block):
    settings: Settings

    @step()
    async def run(self) -> int:
        return 0


def test_plain_port_config_pin_without_default_is_seeded():
    block = SettingsPortBlock()

    assert block.settings.value is None
