import pytest

from smartspace.core import Block, Tool, step
from smartspace.enums import ChannelEvent
from smartspace.models import BlockPinRef, OutputChannelMessage, OutputValue


class TestBlock(Block):
    class TestTool(Tool):
        def run(self, a: int, b: int) -> int: ...

    tool: TestTool

    @step()
    async def run(self, a: int, b: int) -> int:
        await self.tool.call(a, b)
        return a + b


@pytest.mark.asyncio
async def test_chunk_empty_input():
    block = TestBlock()

    result = await block.run(2, 5)
    messages = block.get_messages()

    assert len(messages) == 3
    assert result == 7

    assert messages[0].outputs == [
        OutputValue(
            source=BlockPinRef(
                port="tool",
                pin="a",
            ),
            value=OutputChannelMessage(
                event=ChannelEvent.DATA,
                data=2,
            ),
        ),
        OutputValue(
            source=BlockPinRef(
                port="tool",
                pin="b",
            ),
            value=OutputChannelMessage(
                event=ChannelEvent.DATA,
                data=5,
            ),
        ),
    ]

    assert messages[1].outputs == [
        OutputValue(
            source=BlockPinRef(
                port="run",
                pin="",
            ),
            value=7,
        ),
    ]

    assert messages[2].outputs == [
        OutputValue(
            source=BlockPinRef(
                port="tool",
                pin="a",
            ),
            value=OutputChannelMessage(
                event=ChannelEvent.CLOSE,
                data=None,
            ),
        ),
    ]
