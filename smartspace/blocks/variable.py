from typing import Annotated, Any

from smartspace.core import Block, Config, Output, State, metadata, step
from smartspace.enums import BlockCategory


@metadata(
    description="""The `Variable` block can be used to temporarily hold and output data on command
  
- **Set-and-Get Logic**: This block has three main methods:
  - **`set`**: Stores a new value.
  - **`get`**: Sends the current value out the output.
  - **`setGet`**: Combines setting and sending in a single action, immediately outputting the new value that is set""",
    category=BlockCategory.FUNCTION,
    label="variable storage, data holding, value storage, state management, data persistence",
)
class Variable(Block):
    stickyStore: Annotated[
        Any,
        State(),
    ] = "__undefined__"

    sendNextSet: Annotated[
        bool,
        State(),
    ] = False

    initial_value: Annotated[
        Any,
        Config(),
    ] = None

    output: Output[Any]

    @step()
    async def set(self, set: Any):
        self.stickyStore = set
        if self.sendNextSet:
            self.output.send(self.stickyStore)
            self.sendNextSet = False

    @step()
    async def get(self, get: Any):
        if self.stickyStore == "__undefined__":
            if self.initial_value is not None:
                self.sendNextSet = False
                self.output.send(self.initial_value)
            else:
                self.sendNextSet = True
        else:
            self.sendNextSet = False
            self.output.send(self.stickyStore)

    @step()
    async def set_and_get(self, set_and_get: Any):
        self.sendNextSet = False
        self.stickyStore = set_and_get
        self.output.send(self.stickyStore)
