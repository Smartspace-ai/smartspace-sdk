import inspect
from typing import Annotated, Callable

from pydantic import TypeAdapter
from typing_extensions import get_origin


def _issubclass(cls, base):
    return inspect.isclass(cls) and issubclass(get_origin(cls) or cls, base)


def _get_type_adapter(annotation: type) -> TypeAdapter:
    if get_origin(annotation) is Annotated:
        return TypeAdapter(annotation.__args__[0])
    elif annotation is inspect.Parameter.empty:
        return TypeAdapter(object)
    else:
        return TypeAdapter(annotation)


def get_return_type(callable: Callable):
    signature = inspect.signature(callable)
    return (
        signature.return_annotation
        if signature.return_annotation != signature.empty
        else None
    )


def get_parameter_names_and_types(callable: Callable):
    signature = inspect.signature(callable)
    return [
        (name, param.annotation)
        for name, param in signature.parameters.items()
        if name != "self"
    ]
