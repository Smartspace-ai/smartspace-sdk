import inspect
from typing import Annotated, Any, ClassVar

from smartspace.core import (
    Block,
    BlockFunction,
    Expression,
    Input,
    Templatable,
)
from smartspace.blocks._template_utils import make_jinja_env, wrap_auto_json
from smartspace.utils.utils import _issubclass


def _render_value(env: Any, raw: Any, wrapped_context: dict[str, Any]) -> Any:
    """Render a Templatable value against the context.

    Strings are rendered as Jinja2 templates. Dicts and lists are walked and
    their string leaves rendered, so a dict-typed pin (e.g. HTTP headers) can
    carry templates in its values. Dict keys are never rendered. Anything else
    passes through untouched.
    """
    if isinstance(raw, str):
        return env.from_string(raw).render(**wrapped_context)
    if isinstance(raw, dict):
        return {k: _render_value(env, v, wrapped_context) for k, v in raw.items()}
    if isinstance(raw, list):
        return [_render_value(env, v, wrapped_context) for v in raw]
    return raw


class TemplatableBlock(Block):
    """Base class for blocks that want Jinja2 or JMESPath evaluation applied to
    input pins before each step runs.

    Mark string pins with Templatable() for Jinja2 rendering or Expression()
    for JMESPath evaluation. Both work on class-attribute pins (Config or
    Input) and on @step parameters, and resolve against the variadic named
    `context` port — each connected input becomes a top-level key.

    Dict- and list-typed Templatable pins are walked and their string leaves
    rendered, so e.g. header or query-param dicts can carry templates in
    their values.

    Expression() pins only treat *strings* as expressions — any other value
    (e.g. an object wired straight into the pin) passes through as data.
    Evaluation always runs, context or not: literal-only templates work with
    nothing wired, expressions evaluate against an empty document (missing
    references become null), and a Jinja template referencing an unwired
    context input raises (StrictUndefined) rather than leaking "{{ }}".

    Example:
        class MyBlock(TemplatableBlock):
            prompt: Annotated[str | None, Config(), Templatable()] = None
            # context: ... (inherited — variadic named inputs)

            @step(output_name="response")
            async def run(self, url: Annotated[str, Templatable()]) -> str: ...
    """

    context: dict[str, Annotated[Any, Input()]]

    _templatable_fields: ClassVar[frozenset[str]] = frozenset()
    _expression_fields: ClassVar[frozenset[str]] = frozenset()
    # step/callback port name -> parameter names carrying the marker
    _templatable_step_params: ClassVar[dict[str, frozenset[str]]] = {}
    _expression_step_params: ClassVar[dict[str, frozenset[str]]] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        templatable: set[str] = set()
        expression: set[str] = set()

        for base in reversed(cls.__mro__):
            for field_name, annotation in getattr(base, "__annotations__", {}).items():
                meta = getattr(annotation, "__metadata__", ())
                if any(isinstance(m, Templatable) for m in meta):
                    templatable.add(field_name)
                if any(isinstance(m, Expression) for m in meta):
                    expression.add(field_name)

        cls._templatable_fields = frozenset(templatable)
        cls._expression_fields = frozenset(expression)

        step_templatable: dict[str, frozenset[str]] = {}
        step_expression: dict[str, frozenset[str]] = {}
        for attribute_name in dir(cls):
            attribute = getattr(cls, attribute_name, None)
            if not _issubclass(type(attribute), BlockFunction):
                continue

            t_params: set[str] = set()
            e_params: set[str] = set()
            for p_name, param in inspect.signature(attribute._fn).parameters.items():
                if p_name == "self":
                    continue
                meta = getattr(param.annotation, "__metadata__", ())
                if any(isinstance(m, Templatable) for m in meta):
                    t_params.add(p_name)
                if any(isinstance(m, Expression) for m in meta):
                    e_params.add(p_name)

            if t_params:
                step_templatable[attribute_name] = frozenset(t_params)
            if e_params:
                step_expression[attribute_name] = frozenset(e_params)

        cls._templatable_step_params = step_templatable
        cls._expression_step_params = step_expression

    def __init__(self) -> None:
        super().__init__()
        self._raw_config: dict[str, Any] = {}
        # (port, pin, pin_index) -> raw value, for @step parameters
        self._raw_step_inputs: dict[tuple[str, str, str], Any] = {}
        self.context: dict[str, Any] = {}

    def _set_inputs(self, inputs: list) -> None:
        for iv in inputs:
            field_name = iv.target.port
            if (
                field_name in self._templatable_fields
                or field_name in self._expression_fields
            ) and field_name not in self._raw_config:
                self._raw_config[field_name] = iv.value

            port_name = iv.target.port.split(".")[0]
            t_params = self._templatable_step_params.get(port_name, frozenset())
            e_params = self._expression_step_params.get(port_name, frozenset())
            if t_params or e_params:
                pin_path = iv.target.pin.split(".")
                pin_name = pin_path[0]
                pin_index = pin_path[1] if len(pin_path) > 1 else ""
                if pin_name in t_params or pin_name in e_params:
                    key = (port_name, pin_name, pin_index)
                    if key not in self._raw_step_inputs:
                        self._raw_step_inputs[key] = iv.value

        super()._set_inputs(inputs)

        # Always apply — a template/expression may be entirely literal (no
        # context references), so an empty context must not skip evaluation.
        # The engine delivers all of a run's inputs in a single batch, so a
        # Jinja template referencing an unwired context input fails loudly
        # here (StrictUndefined) instead of leaking "{{ }}" downstream.
        self._apply_templates()

    def _apply_templates(self) -> None:
        from jmespath.exceptions import JMESPathError
        import jmespath
        from smartspace.core import BlockError

        needs_env = bool(self._templatable_fields & self._raw_config.keys()) or any(
            pin_name in self._templatable_step_params.get(port_name, frozenset())
            for port_name, pin_name, _ in self._raw_step_inputs
        )
        if needs_env:
            env = make_jinja_env()
            wrapped = {k: wrap_auto_json(v) for k, v in self.context.items()}

        for field_name in self._templatable_fields:
            raw = self._raw_config.get(field_name)
            if raw is None:
                continue
            try:
                rendered = _render_value(env, raw, wrapped)
            except Exception as e:
                raise BlockError(f"Template rendering failed for '{field_name}': {e}")
            setattr(self, field_name, rendered)

        for field_name in self._expression_fields:
            raw = self._raw_config.get(field_name)
            if raw is None:
                continue
            # Only strings are expressions. A non-string value (e.g. an object
            # wired straight into the pin) is data, not an expression — leave
            # the delivered value in place untouched.
            if not isinstance(raw, str):
                continue
            try:
                result = jmespath.search(raw, self.context)
            except JMESPathError as e:
                raise BlockError(
                    f"Expression evaluation failed for '{field_name}': {e}"
                )
            setattr(self, field_name, result)

        # Step parameters: the engine has already stashed the raw value in the
        # port's pending inputs (BlockFunction._pending_inputs); rewrite it in
        # place so the step receives the rendered value when it runs.
        for (port_name, pin_name, pin_index), raw in self._raw_step_inputs.items():
            if raw is None:
                continue

            if pin_name in self._templatable_step_params.get(port_name, frozenset()):
                try:
                    value = _render_value(env, raw, wrapped)
                except Exception as e:
                    raise BlockError(
                        f"Template rendering failed for '{port_name}.{pin_name}': {e}"
                    )
            else:
                # Only strings are expressions — non-string values (e.g. an
                # object wired straight into the pin) pass through as data.
                if not isinstance(raw, str):
                    continue
                try:
                    value = jmespath.search(raw, self.context)
                except JMESPathError as e:
                    raise BlockError(
                        f"Expression evaluation failed for '{port_name}.{pin_name}': {e}"
                    )

            port = getattr(self, port_name)
            if pin_name not in port._pending_inputs:
                port._pending_inputs[pin_name] = {}
            port._pending_inputs[pin_name][pin_index] = value
