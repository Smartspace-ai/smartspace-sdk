import asyncio
from typing import Annotated, Any

from smartspace.core import Block, Config, Metadata, Output, metadata, step
from smartspace.enums import BlockCategory


@metadata(
    category=BlockCategory.CONTROL,
    icon="fa-hourglass-half",
    label="delay, wait, pause, sleep, timer",
    description=(
        "Waits for the configured number of milliseconds, then forwards the "
        "input data unchanged to the output."
    ),
)
class Delay(Block):
    delay_ms: Annotated[
        int,
        Config(),
        Metadata(description="Delay duration in milliseconds before forwarding the input"),
    ] = 1000

    output: Output[Any]

    @step()
    async def delay(self, data: Any):
        await asyncio.sleep(self.delay_ms / 1000)
        self.output.send(data)
