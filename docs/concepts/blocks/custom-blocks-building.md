This guide will walk you through the steps of creating new blocks for the SmartSpace platform using the provided core block framework. Blocks are reusable components that perform specific tasks in workflows and can be configured with various inputs, outputs, and states.

---

## 1. Block Structure

Blocks are Python classes that inherit from the `Block` base class and optionally from other generic types to support various input and output types. Each block should:

  - Contain inputs and outputs as typed attributes.
  - Implement logic in **steps** or **callbacks**.
  - Optionally use **states** to store intermediate or persistent values.
  - Provide metadata for categorisation and description.

---

## 2. Creating a Simple Block

To create a new block, define a class that extends `Block` and optionally a generic type if needed. You can define the block’s inputs, outputs, and internal logic within the class.

### Example:
```python
from smartspace.core import Block, step

class Count(Block):
    @step(output_name="output")
    async def count(self, items: list[Any]) -> int:
        return len(items)
```

In this example, the `Count` block takes a list of items and outputs the count.

---

## 3. Adding Metadata

You can add metadata to a block to provide descriptive information such as the block’s category, description, or other attributes that are important for its usage in the SmartSpace system. Use the `@metadata` decorator for this purpose.

### Example:
```python
from smartspace.core import Block, metadata, step
from smartspace.enums import BlockCategory

@metadata(
    category=BlockCategory.FUNCTION,
    description="Counts the number of items in a list."
)
class Count(Block):
    @step(output_name="output")
    async def count(self, items: list[Any]) -> int:
        return len(items)
```

The `@metadata` decorator adds useful information for developers and users of the block.

---

## 4. Working with Input and Output Pins

Blocks interact with other blocks via **input** and **output** pins. These pins can be single values, lists, or dictionaries. You can define inputs and outputs using Python type annotations.

### Defining Inputs:
```python
from smartspace.core import Block, step

class Count(Block):
    @step(output_name="output")
    async def count(self, items: list[Any]) -> int:
        return len(items)
```
Here, the `items` parameter is the input, which is a list of any type.

### Defining Outputs:
Outputs are defined similarly to inputs but are typically sent using the `send` method.
```python
class Sum(Block):
    total: Output[int]

    @step()
    async def sum(self, items: list[int]):
        self.total.send(sum(items))
```

---

## 5. Working with States

States in SmartSpace blocks store values that persist across the execution of the block. You can define state variables using the `State` annotation.

### Example:
```python
from typing import Annotated
from smartspace.core import Block, step, State

class Accumulator(Block):
    total: Annotated[int, State(step_id="accumulate", input_ids=["items"])] = 0

    @step()
    async def accumulate(self, items: list[int]):
        self.total += sum(items)
```

In this example, the `total` variable persists across multiple calls to the `accumulate` method.

---

## 6. Defining Block Functions

You can define block functions using the `@step` and `@callback` decorators. Steps are core functions of the block, while callbacks are executed in response to specific events.

### Defining a Step:
```python
class Multiply(Block):
    @step(output_name="result")
    async def multiply(self, x: int, y: int) -> int:
        return x * y
```
Steps are async functions that execute the main logic of the block.

### Defining a Callback:
```python
class MultiplyAndStore(Block):
    @step()
    async def multiply(self, x: int, y: int):
        result = x * y
        await self.store_result(result)

    @callback()
    async def store_result(self, result: int):
        print(f"Result: {result}")
```
Callbacks allow you to define actions that respond to the results of other steps or tools.

---

## 7. Handling Dynamic Inputs and Outputs

In some cases, blocks may need to dynamically handle inputs and outputs at runtime. For example, a block could process a variable number of inputs or outputs. You can define dynamic ports using lists or dictionaries of inputs and outputs.

### Example:
```python
class DynamicBlock(Block):
    dynamic_inputs: list[Input[int]]
    dynamic_outputs: dict[str, Output[int]]

    @step()
    async def process(self):
        for input_value in self.dynamic_inputs:
            output_value = input_value * 2
            self.dynamic_outputs[str(input_value)].send(output_value)
```

---

## 8. Examples

### Example: Map Block
The `Map` block applies a tool to each item in a list and collects the results.

```python
from smartspace.core import Block, Tool, Output, step, callback

class Map(Block):
    class Operation(Tool):
        def run(self, item: int) -> int:
            return item * 2

    results: Output[list[int]]

    @step()
    async def map(self, items: list[int]):
        self.results.send([self.run.call(item) for item in items])
```

### Example: Collect Block
The `Collect` block collects data from a channel and outputs it once the channel closes.

```python
from smartspace.core import Block, InputChannel, Output, step

class Collect(Block):
    items: Output[list[int]]

    @step()
    async def collect(self, item: InputChannel[int]):
        items = []
        while not item.closed:
            data = await item.receive()
            items.append(data)

        self.items.send(items)
```

---

## Conclusion

Blocks in SmartSpace are highly customizable and can be tailored to perform specific tasks within workflows. By following the examples above, you can create new blocks to expand the functionality of the SmartSpace platform. Remember to define inputs, outputs, and states clearly, and use the appropriate decorators (`@step`, `@callback`, `@metadata`) to create powerful and reusable components.