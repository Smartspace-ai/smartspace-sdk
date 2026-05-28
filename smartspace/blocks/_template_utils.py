import json
from typing import Any

from markupsafe import Markup


def make_jinja_env():
    from jinja2.sandbox import SandboxedEnvironment
    from jinja2 import StrictUndefined
    import jmespath
    from jmespath.exceptions import JMESPathError

    env = SandboxedEnvironment(
        loader=None,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    def jmespath_filter(data, expression: str):
        try:
            return jmespath.search(expression, _unwrap(data))
        except JMESPathError as e:
            raise ValueError(f"jmespath filter error: {e}")

    env.filters["jmespath"] = jmespath_filter
    env.globals["jmespath"] = lambda expression, data: jmespath_filter(data, expression)

    return env


def _unwrap(value: Any) -> Any:
    if isinstance(value, AutoJsonDict):
        return {k: _unwrap(v) for k, v in value._data.items()}
    if isinstance(value, AutoJsonList):
        return [_unwrap(i) for i in value._data]
    if isinstance(value, AutoJsonWrapper):
        return value._data
    return value


class AutoJsonWrapper:
    def __init__(self, data: Any):
        self._data = data

    def __str__(self) -> str:
        return Markup(json.dumps(unwrap_for_json(self)))

    def _unwrap(self) -> Any:
        return self._data


class AutoJsonDict(AutoJsonWrapper):
    def __getitem__(self, key: str) -> "AutoJsonWrapper":
        return wrap_auto_json(self._data[key])

    def __getattr__(self, key: str) -> "AutoJsonWrapper":
        return self.__getitem__(key)

    def _unwrap(self) -> dict:
        return {k: unwrap_for_json(v) for k, v in self._data.items()}


class AutoJsonList(AutoJsonWrapper):
    def __getitem__(self, idx: int) -> "AutoJsonWrapper":
        return wrap_auto_json(self._data[idx])

    def __len__(self) -> int:
        return len(self._data)

    def _unwrap(self) -> list:
        return [unwrap_for_json(i) for i in self._data]


class AutoJsonScalar(AutoJsonWrapper):
    def __str__(self) -> str:
        if isinstance(self._data, str):
            return self._data
        return Markup(json.dumps(self._data))


def wrap_auto_json(value: Any) -> AutoJsonWrapper:
    if isinstance(value, dict):
        return AutoJsonDict(value)
    if isinstance(value, list):
        return AutoJsonList(value)
    return AutoJsonScalar(value)


def unwrap_for_json(wrapper: Any) -> Any:
    if isinstance(wrapper, AutoJsonDict):
        return {k: unwrap_for_json(v) for k, v in wrapper._data.items()}
    if isinstance(wrapper, AutoJsonList):
        return [unwrap_for_json(i) for i in wrapper._data]
    if isinstance(wrapper, AutoJsonScalar):
        return wrapper._data
    return wrapper
