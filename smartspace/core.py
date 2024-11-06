import abc
import asyncio
import asyncio.queues
import contextvars
import copy
import enum
import inspect
import json
import types
import typing
from typing import (
    Annotated,
    Any,
    Awaitable,
    Callable,
    ClassVar,
    Concatenate,
    Generic,
    Literal,
    Mapping,
    NamedTuple,
    ParamSpec,
    TypeVar,
    cast,
)

import semantic_version
from more_itertools import first
from pydantic import BaseModel, ConfigDict, TypeAdapter, ValidationError
from pydantic._internal._generics import get_args, get_origin

from smartspace.enums import ChannelEvent
from smartspace.models import (
    BlockErrorModel,
    BlockInterface,
    BlockPinRef,
    BlockRunMessage,
    FlowContext,
    InputChannel,
    InputPinInterface,
    InputValue,
    OutputChannelMessage,
    OutputPinInterface,
    OutputValue,
    PinRedirect,
    PinType,
    PortInterface,
    PortType,
    SmartSpaceWorkspace,
    StateInterface,
    StateValue,
    ThreadMessage,
)
from smartspace.utils import _get_type_adapter, _issubclass

B = TypeVar("B", bound="Block")
S = TypeVar("S")
T = TypeVar("T")
R = TypeVar("R")
P = ParamSpec("P")


def _get_pin_type_from_parameter_kind(kind: inspect._ParameterKind) -> PinType:
    if (
        kind == inspect._ParameterKind.KEYWORD_ONLY
        or kind == inspect._ParameterKind.POSITIONAL_OR_KEYWORD
    ):
        return PinType.SINGLE
    elif kind == inspect._ParameterKind.VAR_POSITIONAL:
        return PinType.LIST
    elif kind == inspect._ParameterKind.VAR_KEYWORD:
        return PinType.DICTIONARY
    else:
        raise Exception(f"Invalid parameter kind {kind}")


class FunctionPins(NamedTuple):
    inputs: dict[str, InputPinInterface]
    input_adapters: dict[str, TypeAdapter]
    output: tuple[OutputPinInterface | None, TypeAdapter | None]
    generics: dict[str, TypeAdapter]


class InputInfo(NamedTuple):
    type: type
    is_channel: bool


def check_type_is_input_channel(annotation: type) -> InputInfo:
    if get_origin(annotation) is InputChannel:
        args = get_args(annotation)
        if not args or len(args) != 1:
            raise Exception("Input channels must have exactly one type.")

        return InputInfo(type=args[0], is_channel=True)
    else:
        return InputInfo(type=annotation, is_channel=False)


def _get_generics(t: type) -> list[TypeVar]:
    bases = getattr(t, "__orig_bases__", None)
    if bases is None or len(bases) == 0:
        return []

    for base in bases:
        if get_origin(base) == Generic:
            return list(get_args(base))

    return []


def _get_function_pins(fn: Callable, port_name: str | None = None) -> FunctionPins:
    signature = inspect.signature(fn)
    inputs: dict[str, InputPinInterface] = {}
    input_adapters: dict[str, TypeAdapter] = {}
    generics: dict[str, TypeAdapter] = {}

    for name, param in signature.parameters.items():
        if name == "self":
            continue

        annotations = getattr(param.annotation, "__metadata__", [])
        metadata = first(
            (metadata.data for metadata in annotations if type(metadata) is Metadata),
            {},
        )

        if param.default == inspect._empty:
            default = None
            required = True
        else:
            default = param.default
            required = False

        input_type, is_channel = check_type_is_input_channel(param.annotation)

        type_adapter, schema, _generics = _get_json_schema_with_generics(input_type)
        generics.update(_generics)

        inputs[name] = InputPinInterface(
            metadata=metadata,
            json_schema=schema,
            sticky=any(
                [metadata.sticky for metadata in annotations if type(metadata) is Input]
            ),
            type=_get_pin_type_from_parameter_kind(param.kind),
            default=default,
            required=required,
            generics={
                name: BlockPinRef(
                    port=port_name if port_name else name,
                    pin=name if port_name else "",
                )
                for name in _generics.keys()
            },
            channel=is_channel,
            virtual=False,
        )
        input_adapters[name] = type_adapter

    if signature.return_annotation != signature.empty:
        annotations = getattr(signature.return_annotation, "__metadata__", [])
        metadata = first(
            (metadata.data for metadata in annotations if type(metadata) is Metadata),
            {},
        )

        if get_origin(signature.return_annotation) == OutputChannel:
            args = get_args(signature.return_annotation)
            if not args or len(args) != 1:
                raise Exception("Outputs must have exactly one type.")

            output_type: type = args[0]
            is_channel = True
        else:
            output_type = signature.return_annotation
            is_channel = False

        output_type_adapter, schema, _generics = _get_json_schema_with_generics(
            output_type
        )
        generics.update(_generics)

        output = (
            OutputPinInterface(
                metadata=metadata,
                json_schema=schema,
                type=PinType.SINGLE,
                generics={
                    name: BlockPinRef(
                        port=port_name if port_name else name,
                        pin=name if port_name else "",
                    )
                    for name in _generics.keys()
                },
                channel=is_channel,
                channel_group_id=port_name if is_channel else None,
            ),
            output_type_adapter,
        )
    else:
        output = (None, None)

    return FunctionPins(
        output=output,
        inputs=inputs,
        input_adapters=input_adapters,
        generics=generics,
    )


class ToolPins(NamedTuple):
    input: tuple[InputPinInterface | None, TypeAdapter | None]
    outputs: dict[str, OutputPinInterface]
    output_adapters: dict[str, TypeAdapter]
    generics: dict[str, TypeAdapter]


def _get_tool_pins(
    fn: Callable,
    port_name: str | None = None,
    generic_names: list[str] | None = None,
) -> ToolPins:
    generic_names = generic_names or []
    signature = inspect.signature(fn)
    outputs: dict[str, OutputPinInterface] = {}
    output_adapters: dict[str, TypeAdapter] = {}
    generics: dict[str, TypeAdapter] = {}

    for name, param in signature.parameters.items():
        if name == "self":
            continue

        annotations = getattr(param.annotation, "__metadata__", [])
        metadata = first(
            (metadata.data for metadata in annotations if type(metadata) is Metadata),
            {},
        )

        output_type = param.annotation

        type_adapter, schema, _generics = _get_json_schema_with_generics(output_type)
        pin_generics: dict[str, BlockPinRef] = {}

        for generic_name in _generics.keys():
            if generic_name in generic_names:
                pin_generics[generic_name] = BlockPinRef(
                    port=port_name if port_name else name,
                    pin=generic_name if port_name else "",
                )
                generics[generic_name] = _generics[generic_name]
            else:
                pin_generics[generic_name] = BlockPinRef(
                    port=generic_name,
                    pin="",
                )

        outputs[name] = OutputPinInterface(
            metadata=metadata,
            json_schema=schema,
            type=_get_pin_type_from_parameter_kind(param.kind),
            generics=pin_generics,
            channel=True,
            channel_group_id=port_name,  # Tool outputs should always be channels so multiple tool calls in a function execution have different scopes
        )

        output_adapters[name] = type_adapter

    if signature.return_annotation != signature.empty:
        annotations = getattr(signature.return_annotation, "__metadata__", [])
        metadata = first(
            (metadata.data for metadata in annotations if type(metadata) is Metadata),
            {},
        )
        input_type, is_channel = check_type_is_input_channel(
            signature.return_annotation
        )

        input_type_adapter, schema, _generics = _get_json_schema_with_generics(
            input_type
        )

        pin_generics: dict[str, BlockPinRef] = {}
        for generic_name in _generics.keys():
            if generic_name in generic_names:
                pin_generics[generic_name] = BlockPinRef(
                    port=port_name if port_name else name,
                    pin=generic_name if port_name else "",
                )
                generics[generic_name] = _generics[generic_name]
            else:
                pin_generics[generic_name] = BlockPinRef(
                    port=generic_name,
                    pin="",
                )

        _input = (
            InputPinInterface(
                metadata=metadata,
                json_schema=schema,
                type=PinType.SINGLE,
                sticky=False,
                required=False,
                default=None,
                generics=pin_generics,
                channel=is_channel,
                virtual=True,
            ),
            input_type_adapter,
        )
    else:
        _input = (None, None)

    return ToolPins(
        outputs=outputs,
        output_adapters=output_adapters,
        input=_input,
        generics=generics,
    )


def _get_default(cls, field_name) -> tuple[bool, Any]:
    no_default = "__no_default__"
    default_value = getattr(cls, field_name, no_default)
    if default_value is not no_default:
        return (True, default_value)

    return (False, None)


class Metadata:
    def __init__(self, **kwargs):
        self.data = kwargs


GenericSchemaT = TypeVar("GenericSchemaT")


class GenericSchema(Generic[GenericSchemaT], dict[str, Any]): ...


class Config: ...


def _get_all_bases(cls: type):
    bases: list[type] = []

    cls_bases = set(
        getattr(cls, "__orig_bases__", tuple())
        + getattr(cls, "__bases__", tuple())
        + getattr(get_origin(cls), "__bases__", tuple())
    )

    for base in cls_bases:
        if base in bases:
            continue

        bases.append(base)
        bases.extend(_get_all_bases(base))

    return bases


def _get_input_pin_from_metadata(
    field_type: type,
    pin_type: PinType,
    port_name: str,
    field_name: str,
    parent: type | None = None,
) -> tuple[tuple[InputPinInterface | None, TypeAdapter | None], dict[str, TypeAdapter]]:
    config: Config | None = None
    _input: Input | None = None
    state: State | None = None
    metadata: dict[str, Any] = {}

    is_input_channel = get_origin(field_type) is InputChannel
    args = get_args(field_type)
    if is_input_channel:
        if not args or len(args) != 1:
            raise Exception("Input channels must have exactly one type.")

        input_type: type = args[0]
    else:
        input_type = field_type if not args or len(args) == 0 else args[0]
        for m in getattr(field_type, "__metadata__", []):
            if isinstance(m, Config):
                config = m

            if isinstance(m, Input):
                _input = m

            if isinstance(m, State):
                state = m

            if isinstance(m, Metadata):
                metadata = m.data

        matches = len([True for i in [config, _input, state] if i is not None])

        if matches > 1:
            raise ValueError(
                "Fields can only be annotated with one of Config(), Input(), and State()"
            )

        if matches == 0:
            return (None, None), {}

        if state:
            return (None, None), {}

        if config and "config" not in metadata:
            metadata["config"] = True

    default = None
    required = True
    if pin_type == PinType.SINGLE:
        if parent is None:
            raise ValueError(
                f"'parent' must be given when getting the interface for a {pin_type} pin"
            )

        has_default, default_value = _get_default(parent, field_name)
        if config and not has_default and input_type is bool:
            default = False
            required = False

        if has_default:
            required = False
            default = default_value

    type_adapter, schema, _generics = _get_json_schema_with_generics(input_type)

    return (
        (
            InputPinInterface(
                metadata=metadata,
                sticky=config is not None or (_input and _input.sticky) or False,
                json_schema=schema,
                type=pin_type,
                generics={
                    name: BlockPinRef(
                        port=name if port_name == field_name else port_name,
                        pin="" if port_name == field_name else name,
                    )
                    for name in _generics.keys()
                },
                default=default,
                required=required,
                channel=is_input_channel,
                virtual=False,
            ),
            type_adapter,
        ),
        _generics,
    )


def _get_state_from_metadata(
    field_type: type,
    field_name: str,
    block_type: "type[Block]",
) -> StateInterface | None:
    state: State | None = None
    metadata: dict[str, Any] = {}

    for m in getattr(field_type, "__metadata__", []):
        if isinstance(m, State):
            state = m

        if isinstance(m, Metadata):
            metadata = m.data

    if state is None:
        return None

    has_default, default = _get_default(block_type, field_name)
    if not has_default:
        raise ValueError("State() attributes must have a default value")

    state_type = get_args(field_type)[0]
    block_type._state_type_adapters[field_name] = _get_type_adapter(state_type)

    return StateInterface(
        metadata=metadata,
        scope=[
            BlockPinRef(port=state.step_id, pin=p)
            for p in state.input_ids or []
            if state.step_id
        ],
        default=default,
    )


def _map_type_vars(
    original_type: type,
    mode: Literal["schema", "validation"],
) -> tuple[type, dict[TypeVar, TypeAdapter]]:
    type_var_defs: dict[TypeVar, TypeAdapter] = {}

    def _inner(new_type: type | TypeVar, depth: int) -> type:
        origin = get_origin(new_type)
        if origin == Annotated:
            args = get_args(new_type)
            if not args:
                return cast(type, new_type)

            new_type = cast(type, args[0])
            return _inner(new_type, depth + 1)

        if isinstance(new_type, TypeVar):

            class TempTypeVarModel2(BaseModel):
                model_config = ConfigDict(title=new_type.__name__)
                if mode == "validation":
                    __pydantic_core_schema__ = {"type": "any"}

            type_var_defs[new_type] = TypeAdapter(new_type)
            return TempTypeVarModel2

        if depth > 10:
            return new_type

        new_args = []
        args = get_args(new_type)
        if args:
            for arg in args:
                if isinstance(arg, TypeVar):
                    if arg not in type_var_defs:

                        class TempTypeVarModel(BaseModel):
                            model_config = ConfigDict(title=arg.__name__)
                            if mode == "validation":
                                __pydantic_core_schema__ = {"type": "any"}

                        type_var_defs[arg] = TypeAdapter(arg)

                    new_args.append(TempTypeVarModel)
                else:
                    new_args.append(_inner(arg, depth + 1))

            if origin:
                if origin is types.UnionType:
                    origin = typing.Union

                class_getitem = getattr(origin, "__class_getitem__", None)
                if class_getitem:
                    n = class_getitem(tuple(new_args))
                    return n

                getitem = getattr(origin, "__getitem__", None)
                if getitem:
                    n = getitem(tuple(new_args))
                    return n

                return new_type
            return new_type

        return new_type

    type_with_generics_replaced = _inner(original_type, 0)
    return type_with_generics_replaced, type_var_defs


class JsonSchemaWithGenerics(NamedTuple):
    type_adapter: TypeAdapter
    schema: dict[str, Any]
    generics: dict[str, TypeAdapter]


def _get_json_schema_with_generics(t: type) -> JsonSchemaWithGenerics:
    new_t, type_var_map = _map_type_vars(t, mode="schema")
    generics = {name.__name__: adapter for name, adapter in type_var_map.items()}
    json_schema = TypeAdapter(Any if new_t == inspect._empty else new_t).json_schema()

    new_t, _ = _map_type_vars(t, mode="validation")
    type_adapter = TypeAdapter(Any if new_t == inspect._empty else new_t)

    if "$defs" in json_schema:
        definitions: dict[str, dict[str, Any]] = json_schema["$defs"]
        new_definitions: dict[str, dict[str, Any]] = {}

        json_schema_str = json.dumps(json_schema)
        for name, definition in definitions.items():
            if "TempTypeVarModel" in name and "title" in definition:
                title = definition["title"]
                new_definitions[title] = {}
                json_schema_str = json_schema_str.replace(name, title)
            else:
                new_definitions[name] = definition

        json_schema = json.loads(json_schema_str)
        json_schema["$defs"] = new_definitions

    elif "title" in json_schema:
        title = json_schema["title"]
        if title in generics:
            json_schema = {"$defs": {title: {}}, "$ref": "#/$defs/" + title}

    return JsonSchemaWithGenerics(
        type_adapter=type_adapter,
        schema=json_schema,
        generics=generics,
    )


class PinsSet(NamedTuple):
    inputs: dict[str, InputPinInterface]
    outputs: dict[str, OutputPinInterface]
    generics: dict[str, TypeAdapter]


def _get_pins(
    cls_annotation: type,
    port_name: str,
    block_type: "type[Block]",
) -> PinsSet:
    cls_metadata = getattr(cls_annotation, "__metadata__", [])
    if len(cls_metadata):
        cls = get_args(cls_annotation)[0]
        metadata = first([a.data for a in cls_metadata if isinstance(a, Metadata)], {})
    else:
        cls = cls_annotation
        metadata = {}

    all_bases = _get_all_bases(cls) + [cls, cls_annotation]

    inputs: dict[str, InputPinInterface] = {}
    outputs: dict[str, OutputPinInterface] = {}
    generics: dict[str, TypeAdapter] = {}

    for base_type in all_bases:
        o = get_origin(base_type)
        if o is Output or o is OutputChannel:
            args = get_args(base_type)
            if not args or len(args) != 1:
                raise Exception("Outputs must have exactly one type.")

            type_adapter, schema, _generics = _get_json_schema_with_generics(args[0])
            generics.update(_generics)

            outputs[""] = OutputPinInterface(
                metadata=metadata,
                json_schema=schema,
                type=PinType.SINGLE,
                generics={
                    name: BlockPinRef(port=name, pin="") for name in _generics.keys()
                },
                channel=o is OutputChannel,
                channel_group_id=f"{port_name}" if o is OutputChannel else None,
            )

    if _issubclass(cls_annotation, Tool):
        tool_type = cast(Tool, cls_annotation)
        generics_on_this_tool = _get_generics(cls_annotation)

        (_input, input_adapter), _outputs, output_adapters, _generics = _get_tool_pins(
            tool_type.run,
            port_name=port_name,
            generic_names=[t.__name__ for t in generics_on_this_tool],
        )

        outputs.update(_outputs)
        for name, adapter in output_adapters.items():
            block_type._set_output_pin_type_adapter(port_name, name, adapter)

        if _input and input_adapter:
            block_type._set_input_pin_type_adapter(port_name, "return", input_adapter)
            inputs["return"] = _input

        for generic_name, generic_schema in _generics.items():
            type_adapter = TypeAdapter(dict[str, Any])
            block_type._set_input_pin_type_adapter(
                port_name, generic_name, type_adapter
            )

            inputs[generic_name] = InputPinInterface(
                metadata={"generic": True, "hidden": True},
                sticky=True,
                json_schema=type_adapter.json_schema(),
                generics={},
                type=PinType.SINGLE,
                required=False,
                default=generic_schema.json_schema(),
                channel=False,
                virtual=False,
            )

    (input_pin, input_adapter), _generics = _get_input_pin_from_metadata(
        base_type,
        port_name=port_name,
        field_name=port_name,
        parent=block_type,
        pin_type=PinType.SINGLE,
    )
    if isinstance(input_pin, InputPinInterface) and input_adapter:
        inputs[""] = input_pin
        block_type._set_input_pin_type_adapter(port_name, "", input_adapter)
        generics.update(_generics)

    annotations = {}
    for base in all_bases:
        annotations.update(getattr(base, "__annotations__", {}))
    annotations.update(**getattr(cls, "__annotations__", {}))

    for field_name, field_annotation in annotations.items():
        field_metadata = getattr(field_annotation, "__metadata__", [])
        if len(field_metadata):
            field_type = get_args(field_annotation)[0]
            metadata = first(
                [a.data for a in field_metadata if isinstance(a, Metadata)], {}
            )
        else:
            metadata = {}
            field_type = field_annotation

        o = get_origin(field_type)
        if o is Output or o is OutputChannel:
            args = get_args(field_type)
            if not args or len(args) != 1:
                raise Exception("Outputs must have exactly one type.")

            type_adapter, schema, _generics = _get_json_schema_with_generics(args[0])
            block_type._set_output_pin_type_adapter(port_name, field_name, type_adapter)
            for generic_name, generic_schema in _generics.items():
                type_adapter = TypeAdapter(dict[str, Any])
                block_type._set_input_pin_type_adapter(
                    port_name, generic_name, type_adapter
                )

                inputs[generic_name] = InputPinInterface(
                    metadata={"generic": True, "hidden": True},
                    sticky=True,
                    json_schema=type_adapter.json_schema(),
                    generics={},
                    type=PinType.SINGLE,
                    required=False,
                    default=generic_schema.json_schema(),
                    channel=False,
                    virtual=False,
                )

            outputs[field_name] = OutputPinInterface(
                metadata=metadata,
                json_schema=schema,
                type=PinType.SINGLE,
                generics={
                    name: BlockPinRef(port=port_name, pin=name)
                    for name in _generics.keys()
                },
                channel=o is OutputChannel,
                channel_group_id=f"{port_name}.{name}" if o is OutputChannel else None,
            )

        elif o is dict:
            dict_args = get_args(field_type)
            if dict_args:
                item_type: type = dict_args[1]

                is_output = _issubclass(item_type, Output)
                is_output_channel = not is_output and _issubclass(
                    item_type, OutputChannel
                )

                if is_output or is_output_channel:
                    if dict_args[0] is not str:
                        raise TypeError("Output dictionaries must have str keys")

                    args = get_args(field_type)
                    if not args or len(args) != 1:
                        raise Exception("Outputs must have exactly one type.")

                    type_adapter, schema, _generics = _get_json_schema_with_generics(
                        args[0]
                    )
                    block_type._set_output_pin_type_adapter(
                        port_name, field_name, type_adapter
                    )
                    for generic_name, generic_schema in _generics.items():
                        type_adapter = TypeAdapter(dict[str, Any])
                        block_type._set_input_pin_type_adapter(
                            port_name, generic_name, type_adapter
                        )

                        inputs[generic_name] = InputPinInterface(
                            metadata={"generic": True, "hidden": True},
                            sticky=True,
                            json_schema=type_adapter.json_schema(),
                            generics={},
                            type=PinType.SINGLE,
                            required=False,
                            default=generic_schema.json_schema(),
                            channel=False,
                            virtual=False,
                        )

                    outputs[field_name] = OutputPinInterface(
                        metadata=metadata,
                        json_schema=schema,
                        type=PinType.DICTIONARY,
                        generics={
                            name: BlockPinRef(port=port_name, pin=name)
                            for name in _generics.keys()
                        },
                        channel=is_output_channel,
                        channel_group_id=f"{port_name}.{name}"
                        if is_output_channel
                        else None,
                    )
                else:
                    (input_pin, input_adapter), _generics = (
                        _get_input_pin_from_metadata(
                            item_type,
                            port_name=port_name,
                            field_name=field_name,
                            parent=cls,
                            pin_type=PinType.DICTIONARY,
                        )
                    )
                    if isinstance(input_pin, InputPinInterface) and input_adapter:
                        block_type._set_input_pin_type_adapter(
                            port_name, field_name, input_adapter
                        )
                        inputs[field_name] = input_pin
                        for generic_name, generic_schema in _generics.items():
                            type_adapter = TypeAdapter(dict[str, Any])
                            block_type._set_input_pin_type_adapter(
                                port_name, generic_name, type_adapter
                            )

                            inputs[generic_name] = InputPinInterface(
                                metadata={"generic": True, "hidden": True},
                                sticky=True,
                                json_schema=type_adapter.json_schema(),
                                generics={},
                                type=PinType.SINGLE,
                                required=False,
                                default=generic_schema.json_schema(),
                                channel=False,
                                virtual=False,
                            )

        elif o is list:
            list_args = get_args(field_type)
            if list_args:
                item_type: type = list_args[0]

                is_output = _issubclass(item_type, Output)
                is_output_channel = not is_output and _issubclass(
                    item_type, OutputChannel
                )

                if is_output or is_output_channel:
                    args = get_args(field_type)
                    if not args or len(args) != 1:
                        raise Exception("Outputs must have exactly one type.")

                    type_adapter, schema, _generics = _get_json_schema_with_generics(
                        args[0]
                    )
                    block_type._set_output_pin_type_adapter(
                        port_name, field_name, type_adapter
                    )

                    for generic_name, generic_schema in _generics.items():
                        type_adapter = TypeAdapter(dict[str, Any])
                        block_type._set_input_pin_type_adapter(
                            port_name, generic_name, type_adapter
                        )

                        inputs[generic_name] = InputPinInterface(
                            metadata={"generic": True, "hidden": True},
                            sticky=True,
                            json_schema=type_adapter.json_schema(),
                            generics={},
                            type=PinType.SINGLE,
                            required=False,
                            default=generic_schema.json_schema(),
                            channel=False,
                            virtual=False,
                        )

                    outputs[field_name] = OutputPinInterface(
                        metadata=metadata,
                        json_schema=schema,
                        type=PinType.LIST,
                        generics={
                            name: BlockPinRef(port=port_name, pin=name)
                            for name in _generics.keys()
                        },
                        channel=is_output_channel,
                        channel_group_id=f"{port_name}.{name}"
                        if is_output_channel
                        else None,
                    )
                else:
                    (input_pin, input_adapter), _generics = (
                        _get_input_pin_from_metadata(
                            item_type,
                            port_name=port_name,
                            field_name=field_name,
                            parent=cls,
                            pin_type=PinType.LIST,
                        )
                    )
                    if isinstance(input_pin, InputPinInterface) and input_adapter:
                        block_type._set_input_pin_type_adapter(
                            port_name, field_name, input_adapter
                        )
                        inputs[field_name] = input_pin
                        for generic_name, generic_schema in _generics.items():
                            type_adapter = TypeAdapter(dict[str, Any])
                            block_type._set_input_pin_type_adapter(
                                port_name, generic_name, type_adapter
                            )

                            inputs[generic_name] = InputPinInterface(
                                metadata={"generic": True, "hidden": True},
                                sticky=True,
                                json_schema=type_adapter.json_schema(),
                                generics={},
                                type=PinType.SINGLE,
                                required=False,
                                default=generic_schema.json_schema(),
                                channel=False,
                                virtual=False,
                            )

        (input_pin, input_adapter), _generics = _get_input_pin_from_metadata(
            field_annotation,
            port_name=port_name,
            field_name=field_name,
            parent=cls,
            pin_type=PinType.SINGLE,
        )
        if isinstance(input_pin, InputPinInterface) and input_adapter:
            inputs[field_name] = input_pin
            block_type._set_input_pin_type_adapter(port_name, field_name, input_adapter)
            for generic_name, generic_schema in _generics.items():
                type_adapter = TypeAdapter(dict[str, Any])
                block_type._set_input_pin_type_adapter(
                    port_name, generic_name, type_adapter
                )

                inputs[generic_name] = InputPinInterface(
                    metadata={"generic": True, "hidden": True},
                    sticky=True,
                    json_schema=type_adapter.json_schema(),
                    generics={},
                    type=PinType.SINGLE,
                    required=False,
                    default=generic_schema.json_schema(),
                    channel=False,
                    virtual=False,
                )

    for field_name, field_annotation in annotations.items():
        field_metadata = getattr(field_annotation, "__metadata__", [])
        if len(field_metadata):
            field_type = get_args(field_annotation)[0]
            metadata = first(
                [a.data for a in field_metadata if isinstance(a, Metadata)], {}
            )
        else:
            metadata = {}
            field_type = field_annotation

        origin = get_origin(field_type)

        if origin is GenericSchema:
            type_var = get_args(field_type)[0]
            generic_name = type_var.__name__
            if generic_name in inputs:
                inputs[field_name] = inputs[generic_name]
                del inputs[generic_name]

            has_default, default = _get_default(block_type, field_name)
            if has_default:
                inputs[field_name].default = default

            inputs[field_name].metadata["hidden"] = False
            inputs[field_name].metadata["config"] = True
            inputs[field_name].metadata.update(metadata)

            block_type._input_pin_type_adapters[port_name][field_name] = (
                block_type._input_pin_type_adapters[port_name][generic_name]
            )
            del block_type._input_pin_type_adapters[port_name][generic_name]

            for pin in list(inputs.values()) + list(outputs.values()):
                for g, pin_ref in pin.generics.items():
                    if (
                        g == generic_name
                        and pin_ref.port == port_name
                        and pin_ref.pin == generic_name
                    ):
                        pin.generics[g] = BlockPinRef(port=port_name, pin=field_name)

    return PinsSet(inputs, outputs, generics)


class PortsAndState(NamedTuple):
    ports: dict[str, PortInterface]
    state: dict[str, StateInterface]


def _get_ports_and_state(block_type: "type[Block]") -> PortsAndState:
    annotations = {}
    for base in _get_all_bases(block_type):
        base_annotations = getattr(base, "__annotations__", {})
        annotations.update(base_annotations)
    annotations.update(**block_type.__annotations__)

    ports: dict[str, PortInterface] = {}
    state: dict[str, StateInterface] = {}
    generics: dict[str, TypeAdapter] = {}

    for port_name, port_annotation in annotations.items():
        port_annotations = getattr(port_annotation, "__metadata__", None)
        if port_annotations:
            field_type = get_args(port_annotation)[0]
            metadata = first(
                [a.data for a in port_annotations if isinstance(a, Metadata)], {}
            )
        else:
            field_type = port_annotation
            metadata = {}

        o = get_origin(field_type)
        if o is dict:
            dict_args = get_args(field_type)
            if dict_args:
                item_type: type = dict_args[1]

                input_pins, output_pins, _generics = _get_pins(
                    item_type, port_name=port_name, block_type=block_type
                )
                if len(input_pins) or len(output_pins):
                    generics.update(_generics)

                    if dict_args[0] is not str:
                        raise TypeError("Port dictionaries must have str keys")

                    port_interface = PortInterface(
                        metadata=metadata,
                        inputs=input_pins,
                        outputs=output_pins,
                        type=PortType.DICTIONARY,
                        is_function=False,
                    )
                    ports[port_name] = port_interface

                    continue

        elif o is list:
            list_args = get_args(field_type)
            if list_args:
                item_type: type = list_args[0]

                input_pins, output_pins, _generics = _get_pins(
                    item_type, port_name=port_name, block_type=block_type
                )
                if len(input_pins) or len(output_pins):
                    generics.update(_generics)
                    port_interface = PortInterface(
                        metadata=metadata,
                        inputs=input_pins,
                        outputs=output_pins,
                        type=PortType.LIST,
                        is_function=False,
                    )
                    ports[port_name] = port_interface

                    continue

        input_pins, output_pins, _generics = _get_pins(
            port_annotation, port_name=port_name, block_type=block_type
        )
        if len(input_pins) or len(output_pins):
            generics.update(_generics)
            port_interface = PortInterface(
                metadata=metadata,
                inputs=input_pins,
                outputs=output_pins,
                type=PortType.SINGLE,
                is_function=False,
            )
            ports[port_name] = port_interface
        else:
            s = _get_state_from_metadata(
                field_type=port_annotation,
                field_name=port_name,
                block_type=block_type,
            )
            if s:
                state[port_name] = s

    for generic_name, generic_schema in generics.items():
        type_adapter = TypeAdapter(dict[str, Any])
        block_type._set_input_pin_type_adapter(generic_name, "", type_adapter)

        ports[generic_name] = PortInterface(
            metadata={},
            inputs={
                "": InputPinInterface(
                    metadata={"generic": True, "hidden": True},
                    sticky=True,
                    json_schema=type_adapter.json_schema(),
                    generics={},
                    type=PinType.SINGLE,
                    required=False,
                    default=generic_schema.json_schema(),
                    channel=False,
                    virtual=False,
                )
            },
            outputs={},
            type=PortType.SINGLE,
            is_function=False,
        )

    return PortsAndState(ports, state)


class Input(BaseModel):
    sticky: bool = False


class State:
    def __init__(
        self,
        step_id: str | None = None,
        input_ids: list[str] | None = None,
    ):
        self.step_id = step_id
        self.input_ids = input_ids


class BlockControlMessage(enum.Enum):
    DONE = "Done"


block_messages: contextvars.ContextVar[
    asyncio.queues.Queue[BlockRunMessage | BlockControlMessage]
] = contextvars.ContextVar("block_messages")


class OutputChannel(Generic[T]):
    def __init__(self, pin: BlockPinRef):
        self.pin = pin

    def send(self, value: T):
        messages = block_messages.get()
        messages.put_nowait(
            BlockRunMessage(
                outputs=[
                    OutputValue(
                        source=self.pin,
                        value=OutputChannelMessage(
                            data=value,
                            event=ChannelEvent.DATA,
                        ),
                    )
                ],
                inputs=[],
                redirects=[],
                states=[],
            )
        )

    def close(self):
        messages = block_messages.get()
        messages.put_nowait(
            BlockRunMessage(
                outputs=[
                    OutputValue(
                        source=self.pin,
                        value=OutputChannelMessage(
                            data=None,
                            event=ChannelEvent.CLOSE,
                        ),
                    )
                ],
                inputs=[],
                redirects=[],
                states=[],
            )
        )


class Output(Generic[T]):
    def __init__(self, pin: BlockPinRef):
        self.pin = pin

    def send(self, value: T):
        messages = block_messages.get()
        messages.put_nowait(
            BlockRunMessage(
                outputs=[
                    OutputValue(
                        source=self.pin,
                        value=value,
                    )
                ],
                inputs=[],
                redirects=[],
                states=[],
            )
        )


class BlockError(Exception):
    def __init__(self, message: str, data: Any = None):
        self.message = message
        self.data = data

    def __str__(self):
        return f"BlockError: {BlockErrorModel(message=self.message, data=self.data)}"


class ReadOnlyDict(Mapping):
    def __init__(self, data):
        self._data = data

    def __getitem__(self, key):
        return self._data[key]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)


class BlockSet:
    def __init__(self):
        self._blocks: dict[str, dict[str, type[Block]]] = {}

    @property
    def all(self) -> "Mapping[str, dict[str, type[Block]]]":
        return ReadOnlyDict(self._blocks)

    def add(self, block: type["Block"]):
        if block.name not in self._blocks:
            self._blocks[block.name] = {}

        self._blocks[block.name][block.version] = block

    def find(self, name: str, version: str):
        spec = semantic_version.NpmSpec(version)
        if name not in self._blocks:
            return None

        versions = {v.semantic_version: v for v in self._blocks[name].values()}
        best_version = spec.select(versions.keys())

        if best_version is None:
            return None

        return versions[best_version]


class MetaBlock(type):
    def __new__(cls, name, bases, attrs):
        block_type = super().__new__(cls, name, bases, attrs)
        block_type.name = block_type.__name__.split("_")[0]

        return block_type

    def __init__(self, name, bases, attrs):
        super().__init__(name, bases, attrs)

        self.metadata: dict[str, Any] = {}
        self.name: str
        self._version: str | None = None
        self._semantic_version: semantic_version.Version | None = None
        self._all_annotations_cache: dict[str, type] | None = None
        self._class_interface: BlockInterface | None = None
        self._input_pin_type_adapters: dict[str, dict[str, TypeAdapter]] = {}
        self._output_pin_type_adapters: dict[str, dict[str, TypeAdapter]] = {}
        self._state_type_adapters: dict[str, TypeAdapter] = {}

    def _set_input_pin_type_adapter(
        self, port: str, pin: str, type_adapter: TypeAdapter
    ):
        if port not in self._input_pin_type_adapters:
            self._input_pin_type_adapters[port] = {}

        self._input_pin_type_adapters[port][pin] = type_adapter

    def _set_output_pin_type_adapter(
        self, port: str, pin: str, type_adapter: TypeAdapter
    ):
        if port not in self._output_pin_type_adapters:
            self._output_pin_type_adapters[port] = {}

        self._output_pin_type_adapters[port][pin] = type_adapter

    def _get_interface(cls):
        if cls._class_interface is None:
            ports, state = _get_ports_and_state(cls)

            for attribute_name in dir(cls):
                attribute = getattr(cls, attribute_name)

                if type(attribute) is Step or type(attribute) is Callback:
                    (inputs, input_adapters, (output, output_adapter), generics) = (
                        _get_function_pins(attribute._fn)
                    )

                    if type(attribute) is Step and output_adapter and output:
                        cls._set_output_pin_type_adapter(
                            attribute_name, attribute._output_name, output_adapter
                        )
                        outputs = {attribute._output_name: output}
                    else:
                        outputs = {}

                    for name, adapter in input_adapters.items():
                        cls._set_input_pin_type_adapter(attribute_name, name, adapter)

                    metadata = attribute.metadata.copy()
                    if type(attribute) is Callback:
                        metadata["callback"] = True
                        metadata["hidden"] = True

                    ports[attribute_name] = PortInterface(
                        metadata=metadata,
                        inputs=inputs,
                        outputs=outputs,
                        type=PortType.SINGLE,
                        is_function=True,
                    )

                    for generic_name, generic_schema in generics.items():
                        type_adapter = TypeAdapter(dict[str, Any])
                        cls._set_input_pin_type_adapter(generic_name, "", type_adapter)

                        ports[generic_name] = PortInterface(
                            metadata={},
                            inputs={
                                "": InputPinInterface(
                                    metadata={"generic": True, "hidden": True},
                                    sticky=True,
                                    json_schema=type_adapter.json_schema(),
                                    generics={},
                                    type=PinType.SINGLE,
                                    required=False,
                                    default=generic_schema.json_schema(),
                                    channel=False,
                                    virtual=False,
                                )
                            },
                            outputs={},
                            type=PortType.SINGLE,
                            is_function=False,
                        )

            annotations = {}
            for base in _get_all_bases(cls):
                base_annotations = getattr(base, "__annotations__", {})
                annotations.update(base_annotations)
            annotations.update(**cls.__annotations__)

            for port_name, port_annotation in annotations.items():
                port_metadata = getattr(port_annotation, "__metadata__", [])
                if len(port_metadata):
                    field_type = get_args(port_annotation)[0]
                    metadata = first(
                        [a.data for a in port_metadata if isinstance(a, Metadata)], {}
                    )
                else:
                    metadata = {}
                    field_type = port_annotation

                origin = get_origin(field_type)

                if origin is GenericSchema:
                    type_var = get_args(field_type)[0]
                    generic_name = type_var.__name__
                    if generic_name in ports:
                        ports[port_name] = ports[generic_name]
                        del ports[generic_name]

                    if port_name in ports:
                        has_default, default = _get_default(cls, port_name)
                        if has_default:
                            ports[port_name].inputs[""].default = default

                        ports[port_name].inputs[""].metadata["hidden"] = False
                        ports[port_name].inputs[""].metadata["config"] = True
                        ports[port_name].inputs[""].metadata.update(metadata)

                        cls._input_pin_type_adapters[port_name] = {
                            "": cls._input_pin_type_adapters[generic_name][""]
                        }
                        del cls._input_pin_type_adapters[generic_name]

                        for port in ports.values():
                            for pin in list(port.inputs.values()) + list(
                                port.outputs.values()
                            ):
                                for g, pin_ref in pin.generics.items():
                                    if (
                                        g == generic_name
                                        and pin_ref.port == generic_name
                                        and pin_ref.pin == ""
                                    ):
                                        pin.generics[g] = BlockPinRef(
                                            port=port_name, pin=""
                                        )

            cls._class_interface = BlockInterface(
                metadata=cls.metadata,
                ports=ports,
                state=state,
            )

        return cls._class_interface

    @property
    def semantic_version(cls):
        if not cls._semantic_version:
            version_str = (
                cls._version or ".".join(cls.__name__.split("_")[1:]) or "1.0.0"
            )
            cls._semantic_version = semantic_version.Version.coerce(version_str)

        return cls._semantic_version

    @property
    def version(cls):
        return str(cls.semantic_version)

    @property
    def _all_annotations(cls):
        if not cls._all_annotations_cache:
            cls._all_annotations_cache = {}
            for base in _get_all_bases(cls):
                base_annotations = getattr(base, "__annotations__", {})
                cls._all_annotations_cache.update(base_annotations)
            cls._all_annotations_cache.update(**cls.__annotations__)

        return cls._all_annotations_cache


def _set_input_pin_value_on_port(
    port: Any,
    pin_name: str,
    pin_index: str | None,
    pin_interface: InputPinInterface,
    value: Any,
):
    if pin_interface.type == PinType.SINGLE:
        setattr(port, pin_name, value)

    elif pin_interface.type == PinType.LIST:
        try:
            pin_index_int = int(pin_index or "")
        except ValueError:
            raise ValueError("Indexes on list Pins must be valid integers")
        pin_list = getattr(port, pin_name, None)
        if not pin_list:
            pin_list = []
            setattr(port, pin_name, pin_list)

        if len(pin_list) < pin_index_int:
            pin_list.extend([None] * (pin_index_int - len(pin_list)))
            pin_list.append(value)
        elif len(pin_list) == pin_index_int:
            pin_list.append(value)
        else:
            pin_list[pin_index_int] = value

    elif pin_interface.type == PinType.DICTIONARY:
        pin_dict = getattr(port, pin_name, None)
        if not pin_dict:
            pin_dict = {}
            setattr(port, pin_name, pin_dict)

        pin_dict[pin_index] = value


class Block(metaclass=MetaBlock):
    error: Annotated[Output[BlockErrorModel], Metadata(hidden=True)]

    def __init__(self):
        self._interface = self.interface()

        self._has_run = False
        self._messages: list[BlockRunMessage] = []
        self._dynamic_ports: dict[str, list[str]] = {}
        self._dynamic_inputs: list[tuple[tuple[str, str], tuple[str, str]]] = []
        self._dynamic_outputs: list[tuple[tuple[str, str], tuple[str, str]]] = []
        self._tools: list[Tool] = []

        for attribute_name in dir(self):
            attribute = getattr(self, attribute_name)

            if _issubclass(type(attribute), BlockFunction):
                new_attribute = attribute.create(self)
                setattr(self, attribute_name, new_attribute)

        self._create_all_ports()

    def _run_function(self, name: str):
        function = getattr(self, name, None)
        if function is None:
            raise ValueError(f"Could not find function '{name}'")

        if not isinstance(function, BlockFunction):
            raise ValueError(f"'{name}' is not a BlockFunction")

        return function._run()

    def _load(
        self,
        context: FlowContext | None = None,
        state: list[StateValue] | None = None,
        inputs: list[InputValue] | None = None,
        dynamic_ports: list[str] | None = None,
        dynamic_output_pins: list[BlockPinRef] | None = None,
        dynamic_input_pins: list[BlockPinRef] | None = None,
    ):
        if (
            (dynamic_input_pins and len(dynamic_input_pins))
            or (dynamic_output_pins and len(dynamic_output_pins))
            or (dynamic_ports and len(dynamic_ports))
        ):
            self._create_all_ports(
                dynamic_ports, dynamic_input_pins, dynamic_output_pins
            )

        if context:
            self._set_context(context)

        if state:
            self._set_state(state)

        if inputs:
            self._set_inputs(inputs)

    def get_messages(self):
        return copy.copy(self._messages)

    @classmethod
    def interface(cls):
        return cls._get_interface().model_copy(deep=True)

    def _create_all_ports(
        self,
        dynamic_ports: list[str] | None = None,
        dynamic_input_pins: list[BlockPinRef] | None = None,
        dynamic_output_pins: list[BlockPinRef] | None = None,
    ):
        for port_name, port_interface in self.interface().ports.items():
            if (
                port_interface.type == PortType.LIST
                or port_interface.type == PortType.DICTIONARY
            ):
                self._dynamic_ports[port_name] = []

        if dynamic_ports:
            for i in dynamic_ports:
                port_path = i.split(".")
                port_name = port_path[0]
                port_index = port_path[1] if len(port_path) == 2 else ""

                if port_index:
                    self._dynamic_ports[port_name].append(port_index)

        if dynamic_input_pins:
            for i in dynamic_input_pins:
                port_path = i.port.split(".")
                pin_path = i.port.split(".")

                port_name = port_path[0]
                port_index = port_path[1] if len(port_path) == 2 else ""

                self._dynamic_inputs.append(
                    (
                        (port_name, port_index),
                        (pin_path[0], pin_path[1] if len(pin_path) == 2 else ""),
                    )
                )

        if dynamic_output_pins:
            for i in dynamic_output_pins:
                port_path = i.port.split(".")
                pin_path = i.port.split(".")

                port_name = port_path[0]
                port_index = port_path[1] if len(port_path) == 2 else ""

                self._dynamic_outputs.append(
                    (
                        (port_name, port_index),
                        (pin_path[0], pin_path[1] if len(pin_path) == 2 else ""),
                    )
                )

        for port_name, port_interface in self.interface().ports.items():
            if port_interface.type == PortType.SINGLE:
                setattr(
                    self,
                    port_name,
                    self._create_port(port_name, ""),
                )

            elif port_interface.type == PortType.LIST:
                port_indexes = [
                    int(port_index) for port_index in self._dynamic_ports[port_name]
                ]

                port_list: list[Any] = [None] * (max(port_indexes, default=-1) + 1)
                for port_index in port_indexes:
                    port_list[port_index] = self._create_port(
                        port_name, str(port_index)
                    )
                setattr(self, port_name, port_list)

            elif port_interface.type == PortType.DICTIONARY:
                port_dict = {
                    port_index: self._create_port(port_name, port_index)
                    for port_index in self._dynamic_ports[port_name]
                }
                setattr(self, port_name, port_dict)

    def _set_context(self, context: FlowContext): ...

    def _set_state(self, state: list[StateValue]):
        for s in state:
            adapter = self.__class__._state_type_adapters[s.state]
            try:
                value = adapter.validate_python(s.value)
            except ValidationError:
                value = s.value

            setattr(self, s.state, value)

    def _set_inputs(self, inputs: list[InputValue]):
        for input_value in inputs:
            port_path = input_value.target.port.split(".")
            port_name = port_path[0]
            if len(port_path) > 1:
                port_index = port_path[1]
            else:
                port_index = ""

            pin_path = input_value.target.pin.split(".")
            pin_name = pin_path[0]
            if len(pin_path) > 1:
                pin_index = pin_path[1]
            else:
                pin_index = ""

            adapter = self.__class__._input_pin_type_adapters[port_name][pin_name]

            try:
                value = adapter.validate_python(input_value.value)
            except ValidationError:
                value = input_value.value

            if (
                port_name in self.interface().ports
                and pin_name in self.interface().ports[port_name].inputs
            ):
                port_interface = self.interface().ports[port_name]
                pin_interface = port_interface.inputs[pin_name]

                if port_interface.is_function:
                    port: BlockFunction = getattr(self, port_name)
                    if pin_name not in port._pending_inputs:
                        port._pending_inputs[pin_name] = {}
                    port._pending_inputs[pin_name][pin_index] = value

                else:
                    if pin_name == "":
                        assert pin_interface.type == PinType.SINGLE

                        if port_interface.type == PortType.SINGLE:
                            setattr(self, port_name, value)

                        elif port_interface.type == PortType.LIST:
                            try:
                                port_index_int = int(port_index)
                            except ValueError:
                                raise ValueError(
                                    "Indexes on list Ports must be valid integers"
                                )

                            port_list: list[Any] = getattr(self, port_name)

                            if len(port_list) < port_index_int:
                                port_list.extend(
                                    [None] * (port_index_int - len(port_list))
                                )
                                port_list.append(value)
                            elif len(port_list) == port_index_int:
                                port_list.append(value)
                            else:
                                port_list[port_index_int] = value

                        elif port_interface.type == PortType.DICTIONARY:
                            port_dict: dict[str, Any] = getattr(self, port_name)
                            port_dict[port_index] = value
                    else:
                        if port_interface.type == PortType.SINGLE:
                            port = getattr(self, port_name)

                        elif port_interface.type == PortType.LIST:
                            try:
                                port_index_int = int(port_index)
                            except ValueError:
                                raise ValueError(
                                    "Indexes on list Ports must be valid integers"
                                )

                            port_list = getattr(self, port_name)
                            port = port_list[port_index_int]

                        elif port_interface.type == PortType.DICTIONARY:
                            port_dict = getattr(self, port_name)
                            port = port_dict[port_index]

                        _set_input_pin_value_on_port(
                            port,
                            pin_name=pin_name,
                            pin_index=pin_index,
                            pin_interface=pin_interface,
                            value=value,
                        )

    def _create_port(
        self,
        port_name: str,
        port_index: str,
    ) -> Any:
        port_id = port_name if not port_index else f"{port_name}.{port_index}"

        port_interface = self.interface().ports[port_name]
        dynamic_inputs: list[tuple[str, str]] = []
        for (_port_name, _port_index), (
            _input_name,
            _input_index,
        ) in self._dynamic_inputs:
            if _port_name == port_name and _port_index == port_index:
                dynamic_inputs.append((_input_name, _input_index))

        dynamic_outputs: list[tuple[str, str]] = []
        for (_port_name, _port_index), (
            _output_name,
            _output_index,
        ) in self._dynamic_outputs:
            if _port_name == port_name and _port_index == port_index:
                dynamic_outputs.append((_output_name, _output_index))

        if len(port_interface.inputs) + len(port_interface.outputs) == 1 and (
            "" in port_interface.inputs or "" in port_interface.outputs
        ):
            if "" in port_interface.inputs:
                input_interface = port_interface.inputs[""]
                type_adapter = self._input_pin_type_adapters[port_name][""]
                return (
                    None
                    if input_interface.default is None
                    else type_adapter.validate_python(input_interface.default)
                )
            elif "" in port_interface.outputs:
                if port_interface.outputs[""].channel:
                    return OutputChannel(BlockPinRef(port=port_id, pin=""))
                else:
                    return Output(BlockPinRef(port=port_id, pin=""))

        tool_port = None
        if port_interface.is_function:
            port = getattr(self, port_name)
        else:
            annotation = self.__class__._all_annotations[port_name]
            if port_interface.type == PortType.SINGLE:
                port_type = annotation
            else:
                if annotation == Annotated:
                    annotation = get_args(annotation)[0]

                if port_interface.type == PortType.LIST:
                    port_type = get_args(annotation)[0]
                elif port_interface.type == PortType.DICTIONARY:
                    port_type = get_args(annotation)[1]

            if _issubclass(port_type, Tool):
                port = port_type(port_name=port_id, input_names=[])
                self._tools.append(port)
                tool_port = cast(Tool, port)
            else:
                port = port_type()

        for input_name, input_interface in port_interface.inputs.items():
            type_adapter = self._input_pin_type_adapters[port_name][input_name]

            if input_interface.type == PinType.SINGLE:
                setattr(
                    port,
                    input_name,
                    None
                    if input_interface.default is None
                    else type_adapter.validate_python(input_interface.default),
                )

            elif input_interface.type == PinType.LIST:
                _dynamic_inputs = [
                    int(index)
                    for _input_name, index in dynamic_inputs
                    if _input_name == input_name
                ]
                inputs = [None] * (max(_dynamic_inputs, default=-1) + 1)

                for index in _dynamic_inputs:
                    inputs[index] = (
                        None
                        if input_interface.default is None
                        else type_adapter.validate_python(input_interface.default)
                    )

                setattr(port, input_name, inputs)

            elif input_interface.type == PinType.DICTIONARY:
                input_dict = {
                    index: None
                    if input_interface.default is None
                    else type_adapter.validate_python(input_interface.default)
                    for _input_name, index in dynamic_inputs
                    if _input_name == input_name
                }

                setattr(port, input_name, input_dict)

        for output_name, output_interface in port_interface.outputs.items():
            if output_interface.type == PinType.SINGLE:
                if output_interface.channel:
                    output = OutputChannel(BlockPinRef(port=port_id, pin=output_name))
                else:
                    output = Output(BlockPinRef(port=port_id, pin=output_name))

                setattr(port, output_name, output)

                if tool_port:
                    tool_port.output_names.append(output_name)

            elif output_interface.type == PinType.LIST:
                _dynamic_outputs = [
                    int(index)
                    for _output_name, index in dynamic_outputs
                    if _output_name == output_name
                ]
                outputs: list[None | Output | OutputChannel] = [None] * (
                    max(_dynamic_outputs, default=-1) + 1
                )

                for index in _dynamic_outputs:
                    if output_interface.channel:
                        outputs[index] = OutputChannel(
                            BlockPinRef(port=port_id, pin=output_name)
                        )
                    else:
                        outputs[index] = Output(
                            BlockPinRef(port=port_id, pin=output_name)
                        )

                setattr(port, output_name, outputs)

                if tool_port:
                    tool_port.output_names.extend(
                        [f"{output_name}.{i}" for i, _ in enumerate(outputs)]
                    )

            elif output_interface.type == PinType.DICTIONARY:
                output_dict: dict[str, Output | OutputChannel] = {
                    index: OutputChannel(BlockPinRef(port=port_id, pin=output_name))
                    if output_interface.channel
                    else Output(BlockPinRef(port=port_id, pin=output_name))
                    for _output_name, index in dynamic_outputs
                    if _output_name == output_name
                }
                setattr(port, output_name, output_dict)

                if tool_port:
                    tool_port.output_names.extend(
                        [f"{output_name}.{i}" for i in output_dict.keys()]
                    )

        return port


class WorkSpaceBlock(Block):
    workspace: SmartSpaceWorkspace
    message_history: list[ThreadMessage]

    def _set_context(self, context: FlowContext):
        assert context.workspace is not None, "Workspace is None in a WorkSpaceBlock"
        assert (
            context.message_history is not None
        ), "Workspace is None in a WorkSpaceBlock"

        self.workspace = context.workspace
        self.message_history = context.message_history


class DummyToolValue: ...


class CallbackCall(NamedTuple):
    name: str
    other_params: dict[str, Any]
    dummy_value_param: str


class ToolCall(Generic[R]):
    def __init__(self, port_name: str, outputs: list[OutputValue]):
        self.port_name = port_name
        self.outputs = outputs
        self.inputs: list[InputValue] = []
        self.redirects: list[PinRedirect] = []

    def then(
        self,
        callback: Callable[[R], CallbackCall],
    ) -> "ToolCall[R]":
        callback_name, other_params, dummy_value_param = callback(
            cast(R, DummyToolValue())
        )

        for name, value in other_params.items():
            self.inputs.append(
                InputValue(
                    target=BlockPinRef(
                        port=callback_name,
                        pin=name,
                    ),
                    value=value,
                )
            )

        self.redirects.append(
            PinRedirect(
                source=BlockPinRef(
                    port=self.port_name,
                    pin="return",
                ),
                target=BlockPinRef(
                    port=callback_name,
                    pin=dummy_value_param,
                ),
            )
        )

        return self

    def __await__(self):
        messages = block_messages.get()

        messages.put_nowait(
            BlockRunMessage(
                outputs=self.outputs,
                inputs=self.inputs,
                redirects=self.redirects,
                states=[],
            )
        )

        yield


class Tool(Generic[P, T], abc.ABC):
    metadata: ClassVar[dict] = {}

    def __init__(self, port_name: str, input_names: list[str]):
        self.port_name = port_name
        self.output_names = input_names

    @abc.abstractmethod
    def run(self, *args: P.args, **kwargs: P.kwargs) -> T: ...

    def call(self, *args: P.args, **kwargs: P.kwargs) -> ToolCall[T]:
        s = inspect.signature(self.__class__.run)
        binding = s.bind(self, *args, **kwargs)
        binding.apply_defaults()

        single_outputs: list[OutputValue] = []
        list_outputs: list[OutputValue] = []
        dictionary_outputs: list[OutputValue] = []

        for name, p in s.parameters.items():
            if name == "self":
                continue

            value = binding.arguments[name]

            if p.kind == p.POSITIONAL_OR_KEYWORD or p.kind == p.KEYWORD_ONLY:
                single_outputs.append(
                    OutputValue(
                        source=BlockPinRef(
                            port=self.port_name,
                            pin=name,
                        ),
                        value=OutputChannelMessage(
                            data=value,
                            event=ChannelEvent.DATA,
                        ),
                    )
                )
            elif p.kind == p.VAR_POSITIONAL:
                for i, v in enumerate(value):
                    list_outputs.append(
                        OutputValue(
                            source=BlockPinRef(
                                port=self.port_name,
                                pin=f"{name}.{i}",
                            ),
                            value=OutputChannelMessage(
                                data=v,
                                event=ChannelEvent.DATA,
                            ),
                        )
                    )
            elif p.kind == p.VAR_KEYWORD:
                value = cast(dict[str, Any], value)
                for i, v in value.items():
                    dictionary_outputs.append(
                        OutputValue(
                            source=BlockPinRef(
                                port=self.port_name,
                                pin=f"{name}.{i}",
                            ),
                            value=OutputChannelMessage(
                                data=v,
                                event=ChannelEvent.DATA,
                            ),
                        )
                    )

        all_outputs = single_outputs + list_outputs + dictionary_outputs

        return ToolCall(port_name=self.port_name, outputs=all_outputs)


class BlockFunctionCall:
    def __init__(
        self,
        values: asyncio.queues.Queue[BlockRunMessage | BlockControlMessage],
        step: Awaitable,
    ):
        self.values = values
        self.step = step
        self.result: Any = None

    def _on_done(self, task: asyncio.Task):
        self.values.put_nowait(BlockControlMessage.DONE)
        if not task.cancelled() and not task.exception():
            self.result = task.result()

    def __aiter__(self):
        self.step_future = asyncio.tasks.ensure_future(self.step)
        self.step_future.add_done_callback(self._on_done)

        return self

    async def __anext__(self):
        value = await self.values.get()

        if isinstance(value, BlockControlMessage):
            if value == BlockControlMessage.DONE:
                exc = self.step_future.exception()
                if exc:
                    raise exc

                raise StopAsyncIteration
            else:
                raise ValueError(f"Unexpected BlockControlMessage {value}")
        elif isinstance(value, BlockRunMessage):
            return value
        else:
            raise ValueError(f"Unexpected BlockMessage {value}")


class BlockFunction(Generic[B, P, T]):
    def __init__(
        self,
        fn: Callable[Concatenate[B, P], Awaitable[T]],
        output_name: str | None = None,
    ):
        self.name = fn.__name__
        self._fn = fn
        self._output_name = output_name or ""
        self.metadata: dict = {}
        self._block: B
        self._pending_inputs: dict[str, dict[str, Any]] = {}

    def create(self, block: Block) -> "BlockFunction":
        if isinstance(self, Callback):
            instance = Callback(self._fn)
        else:
            instance = Step(self._fn, self._output_name)

        instance._block = block
        return instance

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        call = await self._call_inner(*args, **kwargs)

        async for m in call:
            self._block._messages.append(m)

        return call.result

    async def _run(self):
        s = inspect.signature(self._fn)

        positional_inputs: list[Any] = []
        var_positional_inputs: list[Any] = []
        keyword_inputs: dict[str, Any] = {}

        for name, p in s.parameters.items():
            if name == "self" or name not in self._pending_inputs:
                continue

            values = self._pending_inputs[name]

            if p.kind == p.POSITIONAL_OR_KEYWORD or p.kind == p.KEYWORD_ONLY:
                if "" in values:
                    positional_inputs.append(
                        values[""]
                    )  # s.parameters is an ordered dict
            elif p.kind == p.VAR_POSITIONAL:
                indexed_values = {int(index): value for index, value in values.items()}
                var_positional_inputs = [None] * (
                    max(indexed_values.keys(), default=-1) + 1
                )
                for i, v in indexed_values.items():
                    var_positional_inputs[i] = v

            elif p.kind == p.VAR_KEYWORD:
                keyword_inputs.update(values)

        return await self._call_inner(
            *tuple(positional_inputs + var_positional_inputs),
            **keyword_inputs,
        )

    async def _call_inner(self, *args: P.args, **kwargs: P.kwargs) -> BlockFunctionCall:
        if self._block._has_run:
            raise BlockError(
                message="Block has already run a function. Each instance of a block can only run once",
                data={"function_name": self.name},
            )

        self._block._has_run = True

        messages: asyncio.queues.Queue[BlockRunMessage | BlockControlMessage] = (
            asyncio.queues.Queue()
        )
        block_messages.set(messages)

        async def _inner() -> T:
            result = await self._fn(
                self._block,
                *args,
                **kwargs,
            )

            outputs: list[OutputValue] = []
            states: list[StateValue] = []

            s = inspect.signature(self._fn)
            if s.return_annotation is not inspect._empty:
                outputs = [
                    OutputValue(
                        source=BlockPinRef(port=self.name, pin=self._output_name),
                        value=result,
                    )
                ]

            for state_name in self._block._interface.state.keys():
                state_value = getattr(self._block, state_name, None)
                states.append(
                    StateValue(
                        state=state_name,
                        value=state_value,
                    )
                )

            messages.put_nowait(
                BlockRunMessage(
                    outputs=outputs,
                    inputs=[],
                    redirects=[],
                    states=states,
                )
            )

            tool_close_outputs = [
                OutputValue(
                    source=BlockPinRef(
                        port=tool.port_name,
                        pin=tool.output_names[0],
                    ),
                    value=OutputChannelMessage(
                        data=None,
                        event=ChannelEvent.CLOSE,
                    ),
                )
                for tool in self._block._tools
            ]

            messages.put_nowait(
                BlockRunMessage(
                    outputs=tool_close_outputs,
                    inputs=[],
                    redirects=[],
                    states=[],
                )
            )

            return result

        return BlockFunctionCall(
            messages,
            _inner(),
        )


class Step(BlockFunction[B, P, T]):
    def __init__(
        self,
        fn: Callable[Concatenate[B, P], Awaitable[T]],
        output_name: str | None = None,
    ):
        super().__init__(fn)
        self._output_name = output_name or ""


class Callback(BlockFunction[B, P, None]):
    def __init__(
        self,
        fn: Callable[Concatenate[B, P], Awaitable[None]],
    ):
        super().__init__(fn, None)

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
            name=self.name,
            other_params=direct_params,
            dummy_value_param=tool_result_param,
        )


def metadata(**kwargs):
    def _inner(cls):
        setattr(cls, "metadata", kwargs)
        return cls

    return _inner


def version(version: str):
    def inner(cls: type[B]) -> type[B]:
        cls._version = version
        return cls

    return inner


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
        fn: Callable[Concatenate[B, P], Awaitable[None]],
    ) -> Callback[B, P]:
        if not inspect.iscoroutinefunction(fn):
            raise TypeError(f"Callbacks must be async and step {fn.__name__} is not")

        return Callback[B, P](fn)

    return callback_decorator


UserMessageT = TypeVar("UserMessageT")


class User(Block, Generic[UserMessageT]):
    schema: GenericSchema[UserMessageT] = GenericSchema({"type": "string"})
    response: Output[UserMessageT]

    @step()
    async def ask(self, message: str): ...

    @callback()
    async def handle_response(self, response: UserMessageT):
        self.response.send(response)
