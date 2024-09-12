import abc
import asyncio
import inspect
from functools import lru_cache, partial
from typing import (
    Annotated,
    Any,
    Awaitable,
    Callable,
    ClassVar,
    Concatenate,
    Generic,
    ParamSpec,
    Protocol,
    Tuple,
    Type,
    TypeVar,
    cast,
)

from more_itertools import first
from pydantic import BaseModel
from typing_extensions import get_origin

from smartspace.enums import BlockCategory
from smartspace.models import (
    BlockDefinition,
    BlockInterface,
    BlockOutputReference,
    BlockType,
    CallbackCall,
    CallbackInterface,
    ConfigDefinition,
    ConfigInterface,
    FlowContext,
    FlowValue,
    InputDefinition,
    InputInterface,
    OutputDefinition,
    OutputInterface,
    SmartSpaceWorkspace,
    StateInterface,
    StepDefinition,
    StepInterface,
    ToolDefinition,
    ToolInputDefinition,
    ToolInputReference,
    ToolInterface,
    ToolOutputDefinition,
    ValueSourceRef,
    ValueSourceType,
)
from smartspace.utils import _get_type_adapter, _issubclass

B = TypeVar("B", bound="Block")
S = TypeVar("S")
T = TypeVar("T")
R = TypeVar("R")
P = ParamSpec("P")


@lru_cache(maxsize=1000)
def _get_parameter_names_and_types(callable: Callable):
    signature = inspect.signature(callable)
    return {
        name: param.annotation
        for name, param in signature.parameters.items()
        if name != "self"
    }


@lru_cache(maxsize=1000)
def _get_return_type(callable: Callable):
    signature = inspect.signature(callable)
    return (
        signature.return_annotation
        if signature.return_annotation != signature.empty
        else None
    )


def _get_input_interfaces(callable: Callable) -> list["InputInterface"]:
    return [
        InputInterface(
            name=name,
            json_schema=_get_type_adapter(annotation).json_schema(),
            sticky=any(
                [
                    metadata.sticky
                    for metadata in getattr(annotation, "__metadata__", [])
                    if type(metadata) is InputConfig
                ]
            ),
            metadata=first(
                (
                    metadata.data
                    for metadata in getattr(annotation, "__metadata__", [])
                    if type(metadata) is Metadata
                ),
                {},
            ),
        )
        for name, annotation in _get_parameter_names_and_types(callable).items()
    ]


def _get_output_interface(name: str, callable: Callable) -> "OutputInterface | None":
    return_type = _get_return_type(callable)
    if return_type:
        return OutputInterface(
            name=name,
            json_schema=_get_type_adapter(return_type).json_schema(),
        )
    else:
        return None


def _get_configs(cls) -> list["ConfigInterface"]:
    configs: list[ConfigInterface] = []
    for field_name, field_type in cls.__annotations__.items():
        annotations = getattr(field_type, "__metadata__", [])

        for m in annotations:
            if m is ConfigValue:
                if len(field_type.__args__) != 1:
                    raise Exception("Outputs must have exactly one type.")

                metadata = first(
                    (
                        metadata.data
                        for metadata in annotations
                        if type(metadata) is Metadata
                    ),
                    {},
                )

                config_type = field_type.__args__[0]
                type_adapter = _get_type_adapter(config_type)
                no_default = "__no_default__"
                default_value = (
                    getattr(cls, field_name, no_default)
                    or type_adapter.get_default_value()
                )
                if default_value is no_default:
                    try:
                        default_value = type_adapter.dump_python(
                            config_type(), mode="json"
                        )
                    except Exception:
                        default_value = None

                configs.append(
                    ConfigInterface(
                        name=field_name,
                        json_schema=type_adapter.json_schema(),
                        default_value=default_value,
                        metadata=metadata,
                    )
                )

    return configs


def metadata(**kwargs):
    def _inner(cls):
        setattr(cls, "metadata", kwargs)
        return cls

    return _inner


class Metadata:
    def __init__(self, **kwargs):
        self.data = kwargs


class ValueSource:
    def __init__(self, value_callback: Callable[[Any], FlowValue]):
        self.value_callback = value_callback

    def emit(self, value: Any) -> FlowValue:
        return self.value_callback(value)


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
        self.default_value_type_adapter = _get_type_adapter(default_value.__class__)
        self.default_value_json = self.default_value_type_adapter.dump_json(
            default_value
        ).decode()

    def get_default_value(self) -> Any | None:
        return self.default_value_type_adapter.validate_json(self.default_value_json)

    def interface(self, name: str) -> StateInterface:
        return StateInterface(
            name=name,
            step_id=self.step_id,
            input_ids=self.input_ids,
            default_value_json=self.default_value_json,
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
        value_callback: Callable[[Any], FlowValue],
    ):
        ValueSource.__init__(self, value_callback=value_callback)
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
    def __init__(
        self,
        definition: ToolInputDefinition,
        value_callback: Callable[[Any], FlowValue],
    ):
        super().__init__(definition, value_callback=value_callback)
        self.tool_id = definition.tool_id


class RegisterToolCallbackFunction(Protocol):
    def __call__(
        self,
        tool_id: str,
        tool_call_values: list[FlowValue],
        callback: CallbackCall,
    ): ...


class EmitOutputValueFunction(Protocol):
    def __call__(
        self,
        value: Any,
        source: ValueSourceRef,
    ) -> FlowValue: ...


class BlockError(BaseModel):
    message: str
    data: Any = None


class Block:
    metadata: ClassVar[dict] = {}
    error: Output[BlockError]

    def __init__(
        self,
        register_tool_callback: RegisterToolCallbackFunction,
        emit_output_value: EmitOutputValueFunction,
        definition: BlockDefinition | None = None,
        flow_context: FlowContext | None = None,
    ):
        self.add_tool_callback = register_tool_callback
        self.emit_output_value = emit_output_value

        if not definition:
            definition = self.get_default_definition()

        if not flow_context:
            flow_context = FlowContext(
                workspace=SmartSpaceWorkspace(
                    id="test",
                    name="test",
                    data_spaces=[],
                    flow_definition=None,
                ),
                message_history=[],
            )

        self.id = definition.id
        self._definition = definition
        self.workspace = flow_context.workspace
        self.message_history = flow_context.message_history

        self._outputs: dict[str, Output | ToolInput] = {}
        self._steps_instances: dict[str, StepInstance] = {}
        self._tools: dict[str, Tool] = {}

        for state_id, state_definition in definition.states.items():
            value = state_definition.value
            setattr(self, state_id, value)

        for output_name, output_definition in self._definition.outputs.items():
            if type(output_definition) is OutputDefinition:
                cb = partial(
                    self.emit_output_value,
                    source=ValueSourceRef(
                        type=ValueSourceType.BLOCK_OUTPUT,
                        block_output=BlockOutputReference(
                            block_id=self.id,
                            output_id=output_definition.id,
                        ),
                    ),
                )
                self._outputs[output_name] = Output(output_definition, cb)
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
            field_type = self.__class__.__annotations__[config_name]
            config_type = field_type.__args__[0]
            setattr(
                self,
                config_name,
                _get_type_adapter(config_type).validate_python(config_definition.value),
            )

        tool_groups: dict[str, dict[str, Tool]] = {
            field_name: {}
            for field_name, field_type in self.__class__.__annotations__.items()
            if get_origin(field_type) is dict
            and _issubclass(field_type.__args__[1], Tool)
        }

        for tool_name, tool_definition in self._definition.tools.items():
            inputs = {
                name: ToolInput(
                    input_definition,
                    value_callback=partial(
                        self.emit_output_value,
                        source=ValueSourceRef(
                            type=ValueSourceType.TOOL_INPUT,
                            tool_input=ToolInputReference(
                                block_id=self.id,
                                tool_id=tool_name,
                                input_id=name,
                            ),
                        ),
                    ),
                )
                for name, input_definition in tool_definition.inputs.items()
            }
            tool_type = self._get_tool_type(tool_name)
            self._tools[tool_name] = tool_type(
                tool_definition,
                inputs,
                register_tool_callback,
            )

            for tool_input in inputs.values():
                self._outputs[f"{tool_name}.{tool_input.id}"] = tool_input

            tool_path = tool_name.split(".")
            if len(tool_path) == 1:
                setattr(self, tool_name, self._tools[tool_name])
            else:
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
            type=BlockType(
                name=cls.__name__,
                version="dev",
            ),
            configs={},
            outputs={},
            steps={},
            tools={},
            states={},
        )

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
        callbacks: list[CallbackInterface] = []
        tools: list[ToolInterface] = []
        states: list[StateInterface] = []
        configs = _get_configs(cls)

        for field_name, field_type in {
            **cls.__annotations__,
            **Block.__annotations__,
        }.items():
            o = get_origin(field_type)
            if o is Output:
                if len(field_type.__args__) != 1:
                    raise Exception("Outputs must have exactly one type.")

                output_type = field_type.__args__[0]
                outputs.append(
                    OutputInterface(
                        name=field_name,
                        json_schema=_get_type_adapter(output_type).json_schema(),
                    )
                )
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
            else:
                for metadata in getattr(field_type, "__metadata__", []):
                    if type(metadata) is State:
                        states.append(metadata.interface(field_name))
                        break

        for attribute_name in dir(cls):
            attribute = getattr(cls, attribute_name)

            if type(attribute) is Step:
                step_output = attribute.output_interface()
                if step_output:
                    outputs.append(step_output)

                steps.append(attribute.interface())

            if type(attribute) is Callback:
                callbacks.append(attribute.interface())

        block_interface = BlockInterface(
            name=cls.__name__,
            metadata=cls.metadata,
            version=version,
            outputs=outputs,
            steps=steps,
            callbacks=callbacks,
            tools=tools,
            configs=configs,
            states=states,
        )

        return block_interface


class DummyToolValue: ...


class Tool(abc.ABC, Generic[P, T]):
    metadata: ClassVar[dict] = {}

    class ToolCall(Generic[R]):
        def __init__(self, parent: "Tool[P, T]", values: list[FlowValue]):
            self.parent = parent
            self.values = values

        # this provides the ability to await tool calls and get the result, but this is not supported atm because of the complexity of local dev and also because it's not best practice
        # def __await__(self) -> Generator[Any, None, R]:
        #     if not self.parent.output:
        #         return None  # type: ignore

        #     v = yield from self.parent.output.wait(self.values).__await__()
        #     return v  # type: ignore

        def then(
            self,
            callback: Callable[[R], CallbackCall],
        ) -> "Tool.ToolCall[R]":
            callback_call = callback(cast(R, DummyToolValue()))

            self.parent.register_callback(
                tool_id=self.parent.id,
                tool_call_values=self.values,
                callback=callback_call,
            )

            return self

    def __init__(
        self,
        definition: ToolDefinition,
        inputs: dict[str, ToolInput],
        register_callback: RegisterToolCallbackFunction,
    ):
        # tools are triggered by sending values to the outputs and then waiting for a response on the input
        self.id = definition.id
        self.output = ToolOutput[T](definition.output) if definition.output else None
        self.inputs = inputs
        self.register_callback = register_callback

        for config_name, config_definition in definition.configs.items():
            setattr(self, config_name, config_definition.value)

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
            metadata=cls.metadata,
            inputs=_get_input_interfaces(cls.run),
            output=_get_output_interface("return", cls.run),
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
        input_types = self.step.input_types()
        step_kwargs: dict[str, Any] = {}

        for input_name, value in kwargs.items():
            input_type = input_types[input_name]
            step_kwargs[input_name] = _get_type_adapter(input_type).validate_python(
                value
            )

        result = await self.step._fn(self.parent_block, *tuple(), **step_kwargs)
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
        self._output_name = output_name or f"{self.name}.output"
        self.metadata: dict = {}

        class as_tool(Tool):
            def run(self): ...

        setattr(as_tool, "run", fn)
        self.as_tool = as_tool

    def output_interface(self) -> OutputInterface | None:
        return _get_output_interface(self._output_name, self._fn)

    def interface(self) -> StepInterface:
        output_interface = self.output_interface()
        return StepInterface(
            name=self.name,
            inputs=_get_input_interfaces(self._fn),
            output_ref=self._output_name if output_interface else None,
            metadata=self.metadata,
        )

    def input_types(self) -> dict[str, Type]:
        return _get_parameter_names_and_types(self._fn)

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        raise Exception(
            "Invalid step call. Something has gone wrong, Step should be replaced by a callable StepInstance on block instances"
        )


class Callback(Generic[B, P]):
    def __init__(
        self,
        fn: Callable[Concatenate[B, P], Awaitable],
    ):
        self.name = fn.__name__
        self._fn = fn

    def interface(self) -> CallbackInterface:
        return CallbackInterface(
            name=self.name,
            inputs=_get_input_interfaces(self._fn),
        )

    def input_types(self) -> dict[str, Type]:
        return _get_parameter_names_and_types(self._fn)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> CallbackCall:
        values = inspect.getcallargs(self._fn, cast(Block, None), *args, **kwargs)

        tool_result_param = ""
        direct_params: dict[str, Any] = {}

        for arg_name, value in values.items():
            if isinstance(value, DummyToolValue):
                tool_result_param = arg_name
            elif arg_name != "self":
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


def description(text: str):
    def __inner(cls):
        cls.description = text
        return cls

    return __inner


def category(category: BlockCategory):
    def __inner(cls):
        cls.category = category.value
        return cls

    return __inner
