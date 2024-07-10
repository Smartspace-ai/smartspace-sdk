import abc
import asyncio
import inspect
import json
from dataclasses import dataclass
from functools import lru_cache
from typing import (
    Annotated,
    Any,
    Awaitable,
    Callable,
    Concatenate,
    Generator,
    Generic,
    ParamSpec,
    Tuple,
    Type,
    TypeVar,
    cast,
)

from pydantic import BaseModel, TypeAdapter
from typing_extensions import get_origin

from smartspace.models import (
    BlockInterface,
    CallbackCall,
    ConfigInterface,
    FlowValue,
    InputInterface,
    OutputInterface,
    SmartSpaceWorkspace,
    StepInterface,
    ThreadMessage,
    ToolInterface,
)

B = TypeVar("B", bound="Block")
S = TypeVar("S")
T = TypeVar("T")
R = TypeVar("R")
P = ParamSpec("P")


def _issubclass(cls, base):
    return inspect.isclass(cls) and issubclass(get_origin(cls) or cls, base)


@lru_cache(maxsize=1000)
def _get_parameter_names_and_types(callable: Callable):
    signature = inspect.signature(callable)
    return [
        (name, param.annotation)
        for name, param in signature.parameters.items()
        if name != "self"
    ]


@lru_cache(maxsize=1000)
def _get_return_type(callable: Callable):
    signature = inspect.signature(callable)
    return (
        signature.return_annotation
        if signature.return_annotation != signature.empty
        else None
    )


def _get_input_interfaces(callable: Callable) -> dict[str, "InputInterface"]:
    return {
        name: InputInterface(
            name=name,
            json_schema=TypeAdapter(annotation).json_schema(),
            sticky=any(
                [
                    metadata.sticky
                    for metadata in getattr(annotation, "__metadata__", [])
                    if type(metadata) is InputConfig
                ]
            ),
        )
        for name, annotation in _get_parameter_names_and_types(callable)
    }


def _get_output_interface(callable: Callable, name) -> "OutputInterface | None":
    return_type = _get_return_type(callable)
    if return_type:
        return OutputInterface(
            name=name,
            json_schema=TypeAdapter(return_type).json_schema(),
        )
    else:
        return None


def _get_configs(cls) -> list["ConfigInterface"]:
    configs: list[ConfigInterface] = []
    for field_name, field_type in cls.__annotations__.items():
        for m in getattr(field_type, "__metadata__", []):
            if m is ConfigValue:
                if len(field_type.__args__) != 1:
                    raise Exception("Outputs must have exactly one type.")

                config_type = field_type.__args__[0]
                configs.append(
                    ConfigInterface(
                        name=field_name,
                        json_schema=TypeAdapter(config_type).json_schema(),
                    )
                )

    return configs


@dataclass
class InputDefinition:
    id: str
    json_schema: dict[str, Any]
    sticky: bool


@dataclass
class OutputDefinition:
    id: str
    json_schema: dict[str, Any]


@dataclass
class ToolInputDefinition(OutputDefinition):
    tool_id: str


@dataclass
class ToolOutputDefinition:
    id: str
    tool_id: str
    json_schema: dict[str, Any]


@dataclass
class StepDefinition:
    id: str
    inputs: dict[str, InputDefinition]
    output: OutputDefinition | None


@dataclass
class ConfigDefinition:
    id: str
    value: Any


@dataclass
class ToolDefinition:
    id: str
    inputs: dict[str, ToolInputDefinition]
    output: ToolOutputDefinition | None
    configs: dict[str, ConfigDefinition]


@dataclass
class BlockDefinition:
    id: str
    version: str
    configs: dict[str, ConfigDefinition]
    outputs: dict[str, OutputDefinition]
    steps: dict[str, StepDefinition]
    tools: dict[str, ToolDefinition]


class ValueSource:
    def __init__(self):
        self.value_callback: Callable[[Any], FlowValue] | None = None

    def emit(self, value: Any) -> FlowValue:
        if self.value_callback:
            return self.value_callback(value)

        raise Exception("ValueSource must have value_callback set before emitting")


class ConfigValue(
    Generic[T],
):
    def __init__(self, config_definition: ConfigDefinition):
        self.id = config_definition.id
        self.value = config_definition.value


Config = Annotated[T, ConfigValue]


class InputConfig(BaseModel):
    sticky: bool = False


class State:
    def __init__(
        self,
        step_id: str | None = None,
        input_ids: list[str] | None = None,
        default_value: Any | None = None,
    ):
        self.step_id = step_id
        self.input_ids = input_ids
        self.default_value_class = default_value.__class__
        self.default_value_is_pydantic_model = _issubclass(
            self.default_value_class, BaseModel
        )
        self.default_value_json = (
            json.dumps(default_value)
            if not self.default_value_is_pydantic_model
            else cast(BaseModel, default_value).model_dump_json()
        )

    def get_default_value(self) -> Any | None:
        return (
            json.loads(self.default_value_json)
            if not self.default_value_is_pydantic_model
            else cast(type[BaseModel], self.default_value_class).model_validate_json(
                self.default_value_json
            )
        )


class InputSubscription(Generic[T]):
    def __init__(self):
        self.event = asyncio.Event()
        self.value: T = None  # type: ignore


class Input:
    def __init__(self, definition: InputDefinition):
        self.id = definition.id
        self.schema = definition.json_schema
        self.sticky = definition.sticky


class Output(Generic[T], ValueSource):
    def __init__(
        self,
        definition: OutputDefinition,
    ):
        ValueSource.__init__(self)
        self.id = definition.id
        self.schema = definition.json_schema


class ToolOutput(Generic[T]):
    def __init__(
        self,
        definition: ToolOutputDefinition,
    ):
        self.tool_id = definition.tool_id

        self._subscriptions: list[Tuple[list[FlowValue], InputSubscription]] = []

    def check_value(self, value: FlowValue):
        for values, event in self._subscriptions:
            # if value has all values in it's history, then we say it's a response
            if all([value.is_descendant(v) for v in values]):
                event.value = value.value
                event.event.set()

    async def wait(self, sources: list[FlowValue]) -> T:
        subscription = InputSubscription[T]()

        t = (sources, subscription)

        self._subscriptions.append(t)

        await subscription.event.wait()

        self._subscriptions.remove(t)

        return subscription.value


class ToolInput(Output):
    def __init__(self, definition: ToolInputDefinition):
        super().__init__(definition)
        self.tool_id = definition.tool_id


class FlowContext:
    def __init__(
        self,
        workspace: SmartSpaceWorkspace | None,
        message_history: list[ThreadMessage] | None,
    ):
        self.workspace = workspace
        self.message_history = message_history


class Block:
    def __init__(
        self,
        definition: BlockDefinition | None = None,
        states: dict[str, Any] | None = None,
        flow_context: FlowContext | None = None,
    ):
        if not definition:
            definition = self.get_default_definition()

        self.id = definition.id
        self._definition = definition
        self.workspace = flow_context.workspace if flow_context else None
        self.message_history = flow_context.message_history if flow_context else None

        self._outputs: dict[str, Output | ToolInput] = {}
        self._steps_instances: dict[str, StepInstance] = {}
        self._tools: dict[str, Tool] = {}

        if states:
            for state_id, state_value in states.items():
                setattr(self, state_id, state_value)

        for output_name, output_definition in self._definition.outputs.items():
            if type(output_definition) is OutputDefinition:
                self._outputs[output_name] = Output(output_definition)
                setattr(self, output_name, self._outputs[output_name])

        for step_name, step_definition in self._definition.steps.items():
            if step_definition.output:
                output = self._outputs[step_definition.output.id]
            else:
                output = None

            self._steps_instances[step_name] = StepInstance(
                self, step_definition, output
            )

        for config_name, config_definition in self._definition.configs.items():
            setattr(self, config_name, config_definition.value)

        tool_groups: dict[str, dict[str, Tool]] = {}

        for tool_name, tool_definition in self._definition.tools.items():
            inputs = {
                name: ToolInput(input_definition)
                for name, input_definition in tool_definition.inputs.items()
            }
            tool_type = self._get_tool_type(tool_name)
            self._tools[tool_name] = tool_type(tool_definition, inputs)

            for tool_input in inputs.values():
                self._outputs[f"{tool_name}.{tool_input.id}"] = tool_input

            tool_path = tool_name.split(".")
            if len(tool_path) == 1:
                setattr(self, tool_name, self._tools[tool_name])
            else:
                if tool_path[0] not in tool_groups:
                    tool_groups[tool_path[0]] = {}

                tool_groups[tool_path[0]][tool_path[1]] = self._tools[tool_name]

        for (
            tool_attribute_name,
            tool_group,
        ) in tool_groups.items():
            setattr(self, tool_attribute_name, tool_group)

    @classmethod
    def get_default_definition(cls) -> BlockDefinition:
        return BlockDefinition(  # TODO get actual configs, outputs, steps, etc
            id=cls.__name__,
            version="dev",
            configs={},
            outputs={},
            steps={},
            tools={},
        )

    @classmethod
    @lru_cache(maxsize=1000)
    def states(cls) -> dict[str, State]:
        states: dict[str, State] = {}

        for field_name, field_type in cls.__annotations__.items():
            for metadata in getattr(field_type, "__metadata__", []):
                if type(metadata) is State:
                    states[field_name] = metadata
                    break

        return states

    @classmethod
    @lru_cache(maxsize=1)
    def _get_steps(cls) -> dict[str, "Step"]:
        steps: dict[str, Step] = {}

        for attribute_name in dir(cls):
            if attribute_name.startswith("_"):
                continue

            attribute = getattr(cls, attribute_name)

            if type(attribute) is Step:
                steps[attribute_name] = attribute

            elif type(attribute) is Callback:
                steps[attribute_name] = cast(Step, attribute)

        return steps

    def _get_tool_type(self, tool_id: str) -> "type[Tool]":
        attribute_name = tool_id.split(".")[0]
        tool_type = self.__class__.__annotations__[attribute_name]
        if _issubclass(tool_type, Tool):
            return tool_type
        else:
            return tool_type.__args__[1]

    @classmethod
    def interface(cls, version: str = "unknown") -> BlockInterface:
        outputs: list[OutputInterface] = []
        steps: list[StepInterface] = []
        tools: list[ToolInterface] = []
        configs = _get_configs(cls)

        for field_name, field_type in cls.__annotations__.items():
            o = get_origin(field_type)
            if o is Output:
                if len(field_type.__args__) != 1:
                    raise Exception("Outputs must have exactly one type.")

                output_type = field_type.__args__[0]
                output = OutputInterface(
                    name=field_name, json_schema=TypeAdapter(output_type).json_schema()
                )
                outputs.append(output)
            elif _issubclass(field_type, Tool):
                tool_interface = cast(Tool, field_type).interface(field_name, False)
                tools.append(tool_interface)
            elif o is dict:
                assert (
                    field_type.__args__[0] is str
                ), "Tool dictionaries must have string keys"

                item_type: type = field_type.__args__[1]
                if _issubclass(item_type, Tool):
                    tool_interface = cast(Tool, item_type).interface(field_name, True)
                    tools.append(tool_interface)

        for attribute_name in dir(cls):
            if attribute_name.startswith("_"):
                continue

            attribute = getattr(cls, attribute_name)

            if type(attribute) is Step:
                step_output = attribute.output_interface()
                if step_output:
                    outputs.append(step_output)

                steps.append(attribute.interface())

        block_interface = BlockInterface(
            name=cls.__name__,
            version=version,
            outputs=outputs,
            steps=steps,
            tools=tools,
            configs=configs,
        )

        return block_interface


class DummyToolValue: ...


class Tool(abc.ABC, Generic[P, T]):
    class ToolCall(Generic[R]):
        def __init__(self, parent: "Tool[P, T]", values: list[FlowValue]):
            self.parent = parent
            self.values = values

        def __await__(self) -> Generator[Any, None, R]:
            if not self.parent.output:
                return None  # type: ignore

            v = yield from self.parent.output.wait(self.values).__await__()
            return v  # type: ignore

        def then(
            self,
            callback: Callable[[R], CallbackCall],
        ) -> "Tool.ToolCall[R]":
            self.parent._add_callback(self.values, callback(cast(R, DummyToolValue())))

            return self

    def __init__(self, definition: ToolDefinition, inputs: dict[str, ToolInput]):
        # tools are triggered by sending values to the outputs and then waiting for a response on the input
        self.id = definition.id
        self.output = ToolOutput[T](definition.output) if definition.output else None
        self.inputs = inputs

        for config_name, config_definition in definition.configs.items():
            setattr(self, config_name, config_definition.value)

        self._add_callback: Callable[[list[FlowValue], CallbackCall], None] = None  # type: ignore

    def get_input_schema(self):
        """
        Returns a JSON schema for the inputs to the tool.
        """
        schema = {
            "type": "object",
            "properties": {name: i.schema for name, i in self.inputs.items()},
        }

        return schema

    @classmethod
    def interface(cls, name: str, multiple: bool) -> ToolInterface:
        return ToolInterface(
            name=name,
            multiple=multiple,
            inputs=list(_get_input_interfaces(cls.run).values()),
            output=_get_output_interface(cls.run, "return"),
            configs=_get_configs(cls),
        )

    def call(self, *args: P.args, **kwargs: P.kwargs) -> ToolCall[T]:
        # get positional arguments and put them into kwargs
        for i, name in enumerate(self.run.__annotations__.keys()):
            if i < len(args):
                kwargs[name] = args[i]

        # the flow runner will run the tool after we send the values out
        values = [input.emit(kwargs[name]) for name, input in self.inputs.items()]

        return Tool[P, T].ToolCall[T](self, values)

    @abc.abstractmethod
    def run(self, *args: P.args, **kwargs: P.kwargs) -> T: ...


class StepInstance(Generic[B, P, T]):
    def __init__(
        self, parent_block: B, definition: StepDefinition, output: Output[T] | None
    ):
        self.step = cast(Step[B, P, T], getattr(parent_block, definition.id))
        self.output = output
        self.parent_block: B = parent_block

    @property
    def name(self):
        return self.step.name

    async def run(self, *args: P.args, **kwargs: P.kwargs) -> T:
        result = await self.step._fn(self.parent_block, *args, **kwargs)
        if self.output:
            self.output.emit(result)
        return result


class Step(Generic[B, P, T]):
    """
    A step is a process in a block. It is quite generic and can have one or more inputs and can push values to 0 or more outputs while running
    """

    as_tool: Type[Tool[P, T]]

    def __init__(
        self,
        fn: Callable[Concatenate[B, P], Awaitable[T]],
        output_name: str | None = None,
    ):
        self.name = fn.__name__
        self._fn = fn
        self._output_name = output_name

        class as_tool(Tool):
            def run(self): ...

        setattr(as_tool, "run", fn)
        self.as_tool = as_tool

    def output_interface(self) -> OutputInterface | None:
        return _get_output_interface(self._fn, self._output_name or self.name)

    def interface(self) -> StepInterface:
        output_interface = self.output_interface()
        return StepInterface(
            name=self.name,
            inputs=list(_get_input_interfaces(self._fn).values()),
            output_ref=output_interface.name if output_interface else None,
        )

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        raise Exception(
            "Invalid step call. Something has gone wrong, Step should be replaced by a callable StepInstance on block instances"
        )


class Callback(Generic[B, P]):
    def __init__(
        self,
        fn: Callable[Concatenate[B, P], Awaitable[T]],
    ):
        self.name = fn.__name__
        self._fn = fn

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> CallbackCall:
        # get positional arguments and put them into kwargs
        for i, name in enumerate(self._fn.__annotations__.keys()):
            if i < len(args):
                kwargs[name] = args[i]

        tool_result_param = ""
        direct_params: dict[str, Any] = {}

        for arg_name, value in kwargs.items():
            if isinstance(value, DummyToolValue):
                tool_result_param = arg_name
            else:
                direct_params[arg_name] = value

        return CallbackCall(
            callback_name=self.name,
            direct_params=direct_params,
            tool_result_param=tool_result_param,
        )


def step(
    output_name: str | None = None,
) -> Callable[[Callable[Concatenate[B, P], Awaitable[T]]], Step[B, P, T]]:
    def step_decorator(fn: Callable[Concatenate[B, P], Awaitable[T]]) -> Step[B, P, T]:
        if not inspect.iscoroutinefunction(fn):
            raise TypeError(f"Steps must be async and step {fn.__name__} is not")

        return Step[B, P, T](fn, output_name=output_name)

    return step_decorator


def callback() -> Callable[[Callable[Concatenate[B, P], Awaitable]], Callback[B, P]]:
    def callback_decorator(
        fn: Callable[Concatenate[B, P], Awaitable[T]],
    ) -> Callback[B, P]:
        if not inspect.iscoroutinefunction(fn):
            raise TypeError(f"Steps must be async and step {fn.__name__} is not")

        return Callback[B, P](fn)

    return callback_decorator


class User(Block):
    @step(output_name="response")
    async def ask(self, message: str, schema: str) -> Any: ...
