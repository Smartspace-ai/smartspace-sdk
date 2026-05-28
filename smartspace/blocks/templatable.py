from typing import Annotated, Any, ClassVar

from smartspace.core import Block, Expression, Input, Templatable
from smartspace.blocks._template_utils import make_jinja_env, wrap_auto_json


class TemplatableBlock(Block):
    """Base class for blocks that want Jinja2 or JMESPath evaluation applied to
    Config fields before each step runs.

    Mark string Config fields with Templatable() for Jinja2 rendering or
    Expression() for JMESPath evaluation. Both resolve against the variadic
    named `context` port — each connected input becomes a top-level key.

    Example:
        class MyBlock(TemplatableBlock):
            prompt: Annotated[str | None, Config(), Templatable()] = None
            context: ... (inherited — variadic named inputs)
    """

    context: dict[str, Annotated[Any, Input()]]

    _templatable_fields: ClassVar[frozenset[str]] = frozenset()
    _expression_fields: ClassVar[frozenset[str]] = frozenset()

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

    def __init__(self) -> None:
        super().__init__()
        self._raw_config: dict[str, Any] = {}
        self.context: dict[str, Any] = {}

    def _set_inputs(self, inputs: list) -> None:
        for iv in inputs:
            field_name = iv.target.port
            if (
                field_name in self._templatable_fields
                or field_name in self._expression_fields
            ) and field_name not in self._raw_config:
                self._raw_config[field_name] = iv.value

        super()._set_inputs(inputs)

        if self.context:
            self._apply_templates()

    def _apply_templates(self) -> None:
        from jmespath.exceptions import JMESPathError
        import jmespath
        from smartspace.core import BlockError

        if self._templatable_fields & self._raw_config.keys():
            env = make_jinja_env()

        for field_name in self._templatable_fields:
            raw = self._raw_config.get(field_name)
            if raw is None:
                continue
            wrapped = {k: wrap_auto_json(v) for k, v in self.context.items()}
            try:
                rendered = env.from_string(raw).render(**wrapped)
            except Exception as e:
                raise BlockError(f"Template rendering failed for '{field_name}': {e}")
            setattr(self, field_name, rendered)

        for field_name in self._expression_fields:
            raw = self._raw_config.get(field_name)
            if raw is None:
                continue
            try:
                result = jmespath.search(raw, self.context)
            except JMESPathError as e:
                raise BlockError(
                    f"Expression evaluation failed for '{field_name}': {e}"
                )
            setattr(self, field_name, result)
