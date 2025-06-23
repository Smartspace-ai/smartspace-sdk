from typing import Annotated, Any, Generic, TypeVar

from smartspace.core import (
    Block,
    Config,
    Output,
    metadata,
    step,
)
from smartspace.enums import BlockCategory
from smartspace.utils.expressions import evaluate_expression, expression_tooltip

ValueT = TypeVar("ValueT")


@metadata(
    category=BlockCategory.FUNCTION,
    description=f"""Evaluates the input value using the configured condition.
{expression_tooltip}""",
    label="conditional logic, boolean check, if-then-else, branching, condition evaluation",
)
class If(Block, Generic[ValueT]):
    condition: Annotated[str, Config()] = "value"
    false: Output[ValueT]
    true: Output[ValueT]

    @step()
    async def create_response(self, value: ValueT):
        if evaluate_expression(self.condition, value):
            self.true.send(value)
        else:
            self.false.send(value)


class SwitchOption:
    condition: Annotated[str, Config()] = "value == "
    output: Output[Any]


@metadata(
    category=BlockCategory.FUNCTION,
    description=f"""Evaluates the input value using the configured condition.
    {expression_tooltip}""",
    label="switch statement, case selection, multi-way branching, conditional routing, expression switch",
)
class Switch(Block, Generic[ValueT]):
    options: dict[str, SwitchOption]

    @step()
    async def create_response(self, value: ValueT):
        try:
            # Collect all matching options based on the condition.
            matching_options = [
                option
                for option in self.options.values()
                if evaluate_expression(option.condition, value)
            ]

            # Check if exactly one option matched.
            if len(matching_options) != 1:
                raise ValueError(
                    f"Switch error: expected exactly one matching option, but found {len(matching_options)}."
                )

            # Send the output from the single matching option.
            matching_options[0].output.send(value)

        except Exception as error:
            # Handle or re-raise the error as needed.
            raise error


@metadata(
    category=BlockCategory.FUNCTION,
    description=f"""Filters a list of items using the configured condition.
{expression_tooltip}""",
    label="list filtering, item selection, data subsetting, conditional filtering, collection filtering",
)
class Filter(Block, Generic[ValueT]):
    condition: Annotated[str, Config()] = "value"

    @step(output_name="items")
    async def create_response(self, items: list[ValueT]) -> list[ValueT]:
        return [i for i in items if evaluate_expression(self.condition, i)]
