from typing import Annotated, Any, Generic, TypeVar

from smartspace.core import Block, Output, State, step

ValueT = TypeVar("ValueT")


class Buffer(Block, Generic[ValueT]):
    values: Annotated[list[ValueT], State()] = []
    ready: Annotated[bool, State()] = True
    output: Output[ValueT]

    @step()
    async def value(self, value: ValueT):
        self.values.append(value)
        await self._inner()

    @step()
    async def next(self, next: Any):
        self.ready = True
        await self._inner()

    async def _inner(self):
        if not self.ready:
            return

        if len(self.values):
            self.ready = False
            v = self.values.pop(0)
            self.output.send(v)
