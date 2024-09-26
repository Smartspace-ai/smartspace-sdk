This document covers the key concepts that underpin **blocks** in the SmartSpace platform. Blocks are the building blocks of workflows in SmartSpace, and understanding the various concepts around their structure, functionality, and behavior is essential for making the most of the platform.

---

## 1. What are Blocks?

In SmartSpace, **blocks** represent individual units of logic or tasks that execute within a workflow. Each block is a self-contained entity with its own inputs, outputs, states, and functionality, and it interacts with other blocks through defined interfaces.

Blocks are designed to be reusable and modular, allowing complex workflows to be built by combining multiple blocks together. They encapsulate a specific piece of logic, such as counting items, performing mathematical operations, or handling more advanced processing like data collection or transformation.

---

## 2. Block Interfaces

Every block in SmartSpace exposes an **interface**. The interface defines:
- The block's **inputs** and **outputs**, including the type and structure of data that the block can accept or produce.
- The **state** the block maintains across executions.
- The **metadata** that describes the block's functionality and behavior.

The block interface serves as a contract for how the block interacts with the rest of the workflow. When a block is instantiated, its interface allows other blocks or users to understand its available functionalities and how to connect to it.

### Example Interface:
```json
{
  "inputs": {
    "x": "int",
    "y": "int"
  },
  "outputs": {
    "result": "int"
  },
  "state": {
    "total": "int"
  },
  "metadata": {
    "description": "Multiplies two numbers"
  }
}
```

---

## 3. Inputs, Outputs, and Pins

Blocks interact with each other via **pins**, which represent the connection points for **inputs** and **outputs**. Pins allow data to flow between blocks during the execution of a workflow.

### Inputs:
An input is data provided to a block to perform its task. Inputs can be primitive types (like `int`, `str`, etc.) or more complex types (like lists or dictionaries). Inputs are bound to **input pins**.

### Outputs:
Outputs are the result of a block's execution. They are bound to **output pins** and can send data to other blocks in the workflow. Outputs can be a single value or a collection of values.

### 3.1 Pin Types

Pins are of three main types:
- **Single Pins (PinType.SINGLE):** Handle individual values, such as a single integer or string.
- **List Pins (PinType.LIST):** Handle lists of values, such as a list of integers.
- **Dictionary Pins (PinType.DICTIONARY):** Handle key-value pairs where keys are strings and values are complex data types like objects or lists.

Each pin type controls how inputs and outputs are structured and connected.

---

## 4. States

Blocks can maintain **state**, which represents persistent data stored within the block across different executions. States allow a block to retain information between multiple workflow runs.

State variables are defined using the `State` annotation and are useful for keeping track of counters, aggregated data, or other information that needs to be preserved.

### Example:
```python
class Accumulator(Block):
    total: Annotated[int, State(step_id="accumulate", input_ids=["items"])] = 0
```

In this example, the `total` state retains the sum of items processed across multiple steps in the workflow.

---

## 5. Ports

**Ports** are logical groupings of inputs and outputs that allow blocks to manage data flow and interaction. A block can have multiple ports, each responsible for handling different inputs and outputs. Ports can be:
- **Single (PortType.SINGLE):** A port managing a single input/output pair.
- **List (PortType.LIST):** A port handling a list of inputs or outputs.
- **Dictionary (PortType.DICTIONARY):** A port managing key-value pairs for inputs or outputs.

Ports provide an additional level of structure to the inputs and outputs of a block. They make it easier to manage complex blocks that handle multiple data flows.

---

## 6. Steps and Callbacks

**Steps** and **Callbacks** are key concepts in defining a block’s behavior.

### Steps:
A **step** is a function that represents a unit of work performed by the block. It is marked with the `@step` decorator and typically contains the core logic of the block. Steps are asynchronous (`async` functions) and can interact with the block's inputs, outputs, and states.

### Example:
```python
class Multiply(Block):
    @step(output_name="result")
    async def multiply(self, x: int, y: int) -> int:
        return x * y
```

### Callbacks:
A **callback** is a function that is triggered in response to an event, such as receiving data from another block or completing an action. Callbacks are marked with the `@callback` decorator and are also asynchronous.

### Example:
```python
class Collect(Block):
    @callback()
    async def collect(self, result: int):
        print(f"Collected result: {result}")
```

---

## 7. Tools

**Tools** are special types of reusable functionality within a block. A tool allows blocks to perform specific tasks and can be dynamically called with different inputs during a block’s execution. Tools are usually associated with the processing logic applied to inputs.

### Example:
```python
class Operation(Tool):
    def run(self, item: int) -> int:
        return item * 2
```

The `Operation` tool is used to double the value of each input item. Tools make blocks more flexible and reusable, as the same tool can be applied to different sets of data.

---

## 8. Block Metadata

**Metadata** provides descriptive information about a block, such as its category, a human-readable description, and other attributes that help users understand the purpose and behavior of the block.

Metadata is added using the `@metadata` decorator, and it allows blocks to be categorised and documented within the SmartSpace system.

### Example:
```python
@metadata(
    category=BlockCategory.FUNCTION,
    description="Counts the number of items in a list."
)
class Count(Block):
    ...
```

Metadata is crucial for enabling users to search, categorise, and understand blocks within larger workflows.

---

## 9. Dynamic Ports

Some blocks may need to handle dynamic numbers of inputs and outputs that are only known at runtime. These are called **dynamic ports**. Dynamic ports allow a block to accept or produce data based on variable conditions or inputs.

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

In the example above, `dynamic_inputs` and `dynamic_outputs` can handle varying numbers of inputs and outputs.

---

## 10. Error Handling in Blocks

Error handling in blocks is done via the `BlockError` class. This allows blocks to raise and communicate errors during execution. Blocks can define an `error` output pin that emits an error message when a failure occurs.

### Example:
```python
class BlockError(Exception):
    def __init__(self, message: str, data: Any = None):
        self.message = message
        self.data = data

class MyBlock(Block):
    error: Output[BlockError]

    @step()
    async def risky_operation(self):
        try:
            # risky logic here
        except Exception as e:
            self.error.send(BlockError(message=str(e)))
```

Error handling is essential for creating robust blocks that can gracefully handle unexpected situations.

---

## Conclusion

The concepts around blocks in SmartSpace, such as inputs, outputs, states, ports, tools, and metadata, provide a structured and flexible system for creating reusable components in workflows. Understanding these concepts is key to building powerful, dynamic, and scalable workflows using the SmartSpace platform.