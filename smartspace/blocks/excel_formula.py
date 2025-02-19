import re
from typing import Any, Dict

import formulas  # type: ignore
import formulas.tokens
import numpy
from formulas.tokens.operand import XlError

from smartspace.core import Block, metadata, step
from smartspace.enums import BlockCategory

# formulas.get_functions() returns a list of all functions that are supported by the formulas library
VALID_FUNCTIONS = [
    "ISERR",
    "ISODD",
    "ISEVEN",
    "ISERROR",
    "ISNUMBER",
    "ISBLANK",
    "ISTEXT",
    "ISNONTEXT",
    "ISLOGICAL",
    "ISNA",
    "NA",
    "IF",
    "_XLFN.IFS",
    "IFS",
    "IFERROR",
    "_XLFN.IFNA",
    "IFNA",
    "_XLFN.SWITCH",
    "SWITCH",
    "AND",
    "OR",
    "_XLFN.XOR",
    "XOR",
    "NOT",
    "TRUE",
    "FALSE",
    "ABS",
    "ACOS",
    "ACOSH",
    "_XLFN.ACOT",
    "ACOT",
    "ACOTH",
    "_XLFN.ACOTH",
    "_XLFN.ARABIC",
    "ARABIC",
    "ASIN",
    "ASINH",
    "ATAN",
    "ATAN2",
    "ATANH",
    "COS",
    "COSH",
    "COT",
    "_XLFN.COT",
    "COTH",
    "_XLFN.COTH",
    "CSC",
    "_XLFN.CSC",
    "CSCH",
    "_XLFN.CSCH",
    "CEILING",
    "CEILING.MATH",
    "_XLFN.CEILING.MATH",
    "CEILING.PRECISE",
    "_XLFN.CEILING.PRECISE",
    "DEGREES",
    "_XLFN.DECIMAL",
    "DECIMAL",
    "EVEN",
    "EXP",
    "FACT",
    "FACTDOUBLE",
    "FLOOR",
    "_XLFN.FLOOR.MATH",
    "FLOOR.MATH",
    "FLOOR.PRECISE",
    "_XLFN.FLOOR.PRECISE",
    "GCD",
    "INT",
    "ISO.CEILING",
    "LCM",
    "LOG10",
    "LOG",
    "LN",
    "MOD",
    "MROUND",
    "ODD",
    "PI",
    "POWER",
    "RADIANS",
    "RAND",
    "RANDBETWEEN",
    "ROMAN",
    "ROUND",
    "ROUNDDOWN",
    "ROUNDUP",
    "SEC",
    "_XLFN.SEC",
    "SECH",
    "_XLFN.SECH",
    "SIGN",
    "SIN",
    "SINH",
    "SUMPRODUCT",
    "SQRT",
    "SQRTPI",
    "PRODUCT",
    "SUM",
    "SUMIF",
    "SUMSQ",
    "TAN",
    "TANH",
    "TRUNC",
    "AVERAGE",
    "AVERAGEA",
    "AVERAGEIF",
    "CORREL",
    "COUNT",
    "COUNTA",
    "COUNTBLANK",
    "COUNTIF",
    "LARGE",
    "SMALL",
    "MAX",
    "MAXA",
    "MEDIAN",
    "MIN",
    "MINA",
    "SLOPE",
    "_XLFN.FORECAST.LINEAR",
    "FORECAST",
    "FORECAST.LINEAR",
    "_XLFN.NORM.DIST",
    "NORM.DIST",
    "_XLFN.NORM.INV",
    "NORM.INV",
    "_XLFN.NORM.S.DIST",
    "NORM.S.DIST",
    "_XLFN.NORM.S.INV",
    "NORM.S.INV",
    "_XLFN.PERCENTILE.EXC",
    "PERCENTILE.EXC",
    "_XLFN.PERCENTILE.INC",
    "PERCENTILE.INC",
    "_XLFN.QUARTILE.EXC",
    "QUARTILE.EXC",
    "_XLFN.QUARTILE.INC",
    "QUARTILE.INC",
    "_XLFN.STDEV.S",
    "STDEV.S",
    "_XLFN.STDEV.P",
    "STDEV.P",
    "STDEVA",
    "STDEVPA",
    "_XLFN.VAR.S",
    "VAR.S",
    "_XLFN.VAR.P",
    "VAR.P",
    "VARA",
    "VARPA",
    "NPV",
    "XNPV",
    "FV",
    "CUMIPMT",
    "PV",
    "IPMT",
    "PMT",
    "PPMT",
    "RATE",
    "NPER",
    "IRR",
    "XIRR",
    "CHAR",
    "CODE",
    "FIND",
    "LEFT",
    "LEN",
    "LOWER",
    "MID",
    "REPLACE",
    "RIGHT",
    "TRIM",
    "UPPER",
    "SEARCH",
    "_XLFN.CONCAT",
    "CONCAT",
    "CONCATENATE",
    "TEXT",
    "VALUE",
    "COLUMN",
    "ROW",
    "ADDRESS",
    "_XLFN.SINGLE",
    "SINGLE",
    "INDEX",
    "MATCH",
    "LOOKUP",
    "HLOOKUP",
    "VLOOKUP",
    "HEX2OCT",
    "HEX2BIN",
    "HEX2DEC",
    "OCT2HEX",
    "OCT2BIN",
    "OCT2DEC",
    "BIN2HEX",
    "BIN2OCT",
    "BIN2DEC",
    "DEC2HEX",
    "DEC2OCT",
    "DEC2BIN",
    "DATE",
    "DATEVALUE",
    "DAY",
    "MONTH",
    "YEAR",
    "WEEKDAY",
    "_XLFN.ISOWEEKNUM",
    "ISOWEEKNUM",
    "WEEKNUM",
    "DATEDIF",
    "EDATE",
    "TODAY",
    "TIME",
    "TIMEVALUE",
    "SECOND",
    "MINUTE",
    "HOUR",
    "NOW",
    "YEARFRAC",
    "NORMDIST",
    "NORMINV",
    "NORMSDIST",
    "NORMSINV",
    "PERCENTILE",
    "QUARTILE",
    "STDEV",
    "STDEVP",
    "VAR",
    "VARP",
    "__XLUDF.DUMMYFUNCTION",
    "DUMMYFUNCTION",
    "ARRAY",
    "ARRAYROW",
]


@metadata(
    category=BlockCategory.FUNCTION,
    description="Evaluates Excel-like formulas with variable substitution",
    icon="fa-calculator",
)
class ExcelFormula(Block):
    """Block that evaluates Excel-like formulas with variable substitution.

    This block allows you to use Excel-style formulas with variables in double curly braces
    that will be replaced with actual values before evaluation.

    Example:
        Formula: "SUM({{input_a}}, {{input_b}})"
        Variables: {"input_a": 1, "input_b": 2}
        Result: 3

    ## Tested Functions

    ### Basic Arithmetic
    Basic operators: +, -, *, /
    ROUND: Rounds numbers to specified decimal places

    ### Statistical Functions
    SUM: Adds numbers
    AVERAGE: Calculates arithmetic mean
    MAX: Finds highest value
    MIN: Finds lowest value
    COUNT: Counts numbers
    COUNTA: Counts non-empty values
    COUNTBLANK: Counts empty values
    LARGE: Finds nth largest value
    STDEV: Calculates standard deviation
    CORREL: Calculates correlation coefficient
    PERCENTILE: Calculates the nth percentile

    ### Text Functions
    & (operator): String concatenation
    LEFT: Extracts characters from start
    RIGHT: Extracts characters from end
    MID: Extracts characters from middle
    LEN: Returns text length
    UPPER: Converts to uppercase
    LOWER: Converts to lowercase
    TRIM: Removes excess spaces
    FIND: Finds position of substring

    ### Logical Functions
    IF: Conditional logic
    AND: Logical AND
    OR: Logical OR

    ### Date Functions
    TODAY: Current date
    NOW: Current date and time
    DATE: Creates date value

    ### Financial Functions
    PMT: Calculates loan payment
    FV: Future value
    NPV: Net present value

    ### Array Operations
    Array literals: {1,2,3}
    2D arrays: {1,2;3,4}
    """

    def _substitute_variables(self, formula: str, variables: Dict[str, Any]) -> str:
        """Replace variables in the formula with their actual values."""
        pattern = r"\{\{([^}]+)\}\}"

        def replace(match):
            var_name = match.group(1).strip()
            if var_name not in variables:
                raise ValueError(f"Variable '{var_name}' not found in input variables")
            value = variables[var_name]

            # Handle array inputs
            if isinstance(value, (list, tuple)):
                # Handle nested arrays (2D arrays)
                if value and isinstance(value[0], (list, tuple)):
                    # Convert 2D array to Excel format: {row1;row2;...}
                    rows = []
                    for row in value:
                        # Quote strings in arrays
                        row_values = [
                            f'"{x}"' if isinstance(x, str) else str(x) for x in row
                        ]
                        rows.append(",".join(row_values))
                    return "{" + ";".join(rows) + "}"
                else:
                    # For 1D arrays, wrap in curly braces and join with commas
                    values = [f'"{x}"' if isinstance(x, str) else str(x) for x in value]
                    return "{" + ",".join(values) + "}"
            # Quote non-array string values
            if isinstance(value, str):
                return f'"{value}"'
            return str(value)

        return re.sub(pattern, replace, formula)

    @step(output_name="result")
    async def evaluate(self, formula: str, variables: Dict[str, Any]) -> Any:
        """Evaluate an Excel formula with variable substitution.

        Args:
            formula: The Excel formula with variables in double curly braces.
                Example: "SUM({{input_a}}, {{input_b}})"
            variables: Dictionary of variable names and their values.
                Example: {"input_a": 1, "input_b": 2}

        Returns:
            The result of the formula evaluation.

        Raises:
            ValueError: If a variable in the formula is not found in the variables dict
                       or if the formula is invalid.
        """
        try:
            # Replace variables with their values
            processed_formula = self._substitute_variables(formula, variables)

            # Ensure formula starts with =
            if not processed_formula.startswith("="):
                processed_formula = "=" + processed_formula

            # Parse and compile the formula
            func = formulas.Parser().ast(processed_formula)[1].compile()

            # Evaluate the formula
            result = func()
            if isinstance(result, numpy.ndarray):
                # Convert numpy array to list
                nlist = result.tolist()
                if isinstance(nlist, XlError):
                    raise ValueError(f"Error evaluating formula: {str(nlist)}")
                return nlist
            elif isinstance(result, XlError):
                raise ValueError(f"Error evaluating formula: {str(result)}")
            return result

        except Exception as e:
            raise ValueError(f"Error evaluating formula: {str(e)}")
