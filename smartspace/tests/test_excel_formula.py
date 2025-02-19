import pytest

from smartspace.blocks.excel_formula import ExcelFormula


class TestBasicArithmetic:
    @pytest.mark.asyncio
    async def test_addition(self):
        """Test addition operation."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate("{{a}} + {{b}}", {"a": 1, "b": 2})
        assert result == 3.0

    @pytest.mark.asyncio
    async def test_multiplication(self):
        """Test multiplication operation."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate("{{x}} * {{y}}", {"x": 4, "y": 5})
        assert result == 20.0

    @pytest.mark.asyncio
    async def test_division(self):
        """Test division operation."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate("{{n}} / {{m}}", {"n": 10, "m": 2})
        assert result == 5.0

    @pytest.mark.asyncio
    async def test_complex_expression(self):
        """Test complex arithmetic expression."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            "({{a}} + {{b}}) * {{c}}", {"a": 1, "b": 2, "c": 3}
        )
        assert result == 9.0

    @pytest.mark.asyncio
    async def test_round(self):
        """Test ROUND function."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            "ROUND({{number}}, 2)", {"number": 123.4567}
        )
        assert result == 123.46

    @pytest.mark.asyncio
    async def test_round_negative_places(self):
        """Test ROUND function with negative decimal places."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate("ROUND({{number}}, -2)", {"number": 12345})
        assert result == 12300


class TestExcelFunctions:
    @pytest.mark.asyncio
    async def test_sum(self):
        """Test SUM function."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            "SUM({{numbers}})", {"numbers": [1, 2, 3, 4, 5]}
        )
        assert result == 15.0

    @pytest.mark.asyncio
    async def test_average(self):
        """Test AVERAGE function."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            "AVERAGE({{values}})", {"values": [10, 20, 30, 40, 50]}
        )
        assert result == 30.0

    @pytest.mark.asyncio
    async def test_max(self):
        """Test MAX function."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate("MAX({{data}})", {"data": [1, 5, 3, 7, 2]})
        assert result == 7

    @pytest.mark.asyncio
    async def test_min(self):
        """Test MIN function."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate("MIN({{data}})", {"data": [1, 5, 3, 7, 2]})
        assert result == 1

    @pytest.mark.asyncio
    async def test_count_numbers(self):
        """Test COUNT function with pure numbers."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            "COUNT({{data}})", {"data": [1, 2, 3, 4, 5]}
        )
        assert result == 5

    @pytest.mark.asyncio
    async def test_counta(self):
        """Test COUNTA function that counts non-empty cells."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            "COUNTA({{data}})", {"data": [1, "text", True, 5]}
        )
        assert result == 4  # Counts everything except None/empty

    @pytest.mark.asyncio
    async def test_countblank(self):
        """Test COUNTBLANK function."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            "COUNTBLANK({{data}})", {"data": [1, "text", 5, ""]}
        )
        assert result == 1  # Counts only None/empty values


class TestLogicalFunctions:
    @pytest.mark.asyncio
    async def test_if_true_condition(self):
        """Test IF function with true condition."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            'IF({{value}} > 10, "High", "Low")', {"value": 15}
        )
        assert result == "High"

    @pytest.mark.asyncio
    async def test_if_false_condition(self):
        """Test IF function with false condition."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            'IF({{value}} > 10, "High", "Low")', {"value": 5}
        )
        assert result == "Low"

    @pytest.mark.asyncio
    async def test_and_function(self):
        """Test AND function."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            "AND({{a}} > 0, {{b}} < 10)", {"a": 5, "b": 7}
        )
        assert result == True

    @pytest.mark.asyncio
    async def test_or_function(self):
        """Test OR function."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            "OR({{x}} < 0, {{y}} > 10)", {"x": -1, "y": 5}
        )
        assert result == True


class TestTextFunctions:
    @pytest.mark.asyncio
    async def test_string_concatenation(self):
        """Test string concatenation using & operator."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            '{{text1}} & " " & {{text2}}',
            {"text1": "Hello", "text2": "World"},
        )
        assert result == "Hello World"

    @pytest.mark.asyncio
    async def test_len(self):
        """Test LEN function."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate("LEN({{text}})", {"text": "Hello"})
        assert result == 5

    @pytest.mark.asyncio
    async def test_upper(self):
        """Test UPPER function."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate("UPPER({{text}})", {"text": "hello"})
        assert result == "HELLO"

    @pytest.mark.asyncio
    async def test_format_phone_number(self):
        """Test formatting a phone number using string concatenation."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            '"(" & LEFT({{phone}}, 3) & ") " & MID({{phone}}, 4, 3) & "-" & RIGHT({{phone}}, 4)',
            {"phone": "1234567890"},
        )
        assert result == "(123) 456-7890"

    @pytest.mark.asyncio
    async def test_extract_first_name(self):
        """Test extracting first name from a full name."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            'LEFT({{full_name}}, FIND(" ", {{full_name}}) - 1)',
            {"full_name": "John Smith"},
        )
        assert result == "John"

    @pytest.mark.asyncio
    async def test_extract_last_name(self):
        """Test extracting last name from a full name."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            'RIGHT({{full_name}}, LEN({{full_name}}) - FIND(" ", {{full_name}}))',
            {"full_name": "John Smith"},
        )
        assert result == "Smith"

    @pytest.mark.asyncio
    async def test_trim(self):
        """Test TRIM function."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            "TRIM({{text}})", {"text": "   hello   world   "}
        )
        assert result == "hello   world"

    @pytest.mark.asyncio
    async def test_lower(self):
        """Test LOWER function."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate("LOWER({{text}})", {"text": "HELLO World"})
        assert result == "hello world"


class TestErrorHandling:
    @pytest.mark.asyncio
    async def test_missing_variable(self):
        """Test error handling for missing variable."""
        excel_block = ExcelFormula()
        with pytest.raises(ValueError) as exc_info:
            await excel_block.evaluate("{{missing}} + 1", {})
        assert "Variable 'missing' not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_invalid_formula(self):
        """Test error handling for invalid formula."""
        excel_block = ExcelFormula()
        with pytest.raises(ValueError) as exc_info:
            await excel_block.evaluate("INVALID({{x}})", {"x": 1})
        assert "Error evaluating formula" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_division_by_zero(self):
        """Test error handling for division by zero."""
        excel_block = ExcelFormula()
        with pytest.raises(ValueError) as exc_info:
            await excel_block.evaluate("{{a}} / {{b}}", {"a": 1, "b": 0})
        assert "Error evaluating formula" in str(exc_info.value)


class TestArrayHandling:
    @pytest.mark.asyncio
    async def test_array_input(self):
        """Test array input handling."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            "SUM({{array}})", {"array": [[1, 2], [3, 4]]}
        )
        assert result == 10.0

    @pytest.mark.asyncio
    async def test_nested_sum(self):
        """Test nested SUM operations with arrays."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            "SUM(SUM({{array1}}), SUM({{array2}}))",
            {"array1": [[1, 2], [3, 4]], "array2": [[5, 6], [7, 8]]},
        )
        assert result == 36.0  # (1+2+3+4) + (5+6+7+8)

    @pytest.mark.asyncio
    async def test_sum_with_ranges(self):
        """Test SUM with multiple array inputs."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            "SUM({{array1}}, {{array2}})", {"array1": [1, 2, 3], "array2": [4, 5, 6]}
        )
        assert result == 21.0  # 1+2+3+4+5+6

    @pytest.mark.asyncio
    async def test_complex_nested_sum(self):
        """Test complex nested SUM operations with mixed arrays."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            "SUM(SUM({{array1}}), {{single}}, SUM({{array2}}))",
            {"array1": [[1, 2], [3, 4]], "single": 10, "array2": [5, 6, 7, 8]},
        )
        assert result == 46.0  # (1+2+3+4) + 10 + (5+6+7+8)


class TestFinancialCalculations:
    @pytest.mark.asyncio
    async def test_loan_payment(self):
        """Test monthly loan payment calculation using PMT."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            "PMT({{rate}}/12, {{periods}}*12, {{principal}})",
            {"rate": 0.05, "periods": 30, "principal": 300000},
        )
        assert isinstance(result, float)
        assert round(result, 2) == -1610.46

    @pytest.mark.asyncio
    async def test_future_value(self):
        """Test future value calculation of an investment."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            "FV({{rate}}/12, {{periods}}*12, -{{payment}}, {{present_value}})",
            {
                "rate": 0.06,
                "periods": 10,
                "payment": 200,
                "present_value": 1000,
            },
        )
        assert isinstance(result, float)

    @pytest.mark.asyncio
    async def test_net_present_value(self):
        """Test NPV calculation for a series of cash flows."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            "NPV({{rate}}, {{cash_flows}})",
            {"rate": 0.1, "cash_flows": [-1000, 200, 300, 400, 500]},
        )
        assert isinstance(result, float)


class TestStatisticalCalculations:
    @pytest.mark.asyncio
    async def test_percentile(self):
        """Test calculating percentile of a dataset."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            "PERCENTILE({{data}}, 0.9)",
            {"data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]},
        )
        assert isinstance(result, float)
        assert round(result, 2) == 9.10

    @pytest.mark.asyncio
    async def test_standard_deviation(self):
        """Test calculating standard deviation."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            "STDEV({{data}})",
            {"data": [2, 4, 6, 8, 10]},
        )
        assert isinstance(result, float)
        assert round(result, 2) == 3.16

    @pytest.mark.asyncio
    async def test_correlation(self):
        """Test calculating correlation between two datasets."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            "CORREL({{data1}}, {{data2}})",
            {
                "data1": [1, 2, 3, 4, 5],
                "data2": [2, 4, 6, 8, 10],
            },
        )
        assert isinstance(result, float)
        assert round(result, 1) == 1.0

    @pytest.mark.asyncio
    async def test_average(self):
        """Test calculating average of numbers."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            "AVERAGE({{data}})",
            {"data": [1, 2, 3, 4, 5, 6, 7, 8, 9]},
        )
        assert isinstance(result, float)
        assert result == 5.0

    @pytest.mark.asyncio
    async def test_count(self):
        """Test counting numbers in a dataset."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            "COUNT({{data}})",
            {"data": [1, 2, 3, 4, 5, 6, 7, 8, 9]},
        )
        assert result == 9

    @pytest.mark.asyncio
    async def test_sum_large_values(self):
        """Test summing the largest values in a dataset."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            "SUM(LARGE({{data}}, {1,2,3,4}))",  # Sum of 4 largest values
            {"data": [1, 2, 3, 4, 5, 6, 7, 8, 9]},
        )
        assert result == 30  # 9 + 8 + 7 + 6


class TestBusinessCalculations:
    @pytest.mark.asyncio
    async def test_discount_calculation(self):
        """Test calculating discounted price."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            "ROUND({{original_price}} * (1 - {{discount_percent}}), 2)",
            {"original_price": 99.99, "discount_percent": 0.2},
        )
        assert result == 79.99

    @pytest.mark.asyncio
    async def test_markup_calculation(self):
        """Test calculating selling price with markup."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            "ROUND({{cost}} * (1 + {{markup_percent}}), 2)",
            {"cost": 50, "markup_percent": 0.4},
        )
        assert result == 70.00

    @pytest.mark.asyncio
    async def test_tax_calculation(self):
        """Test calculating total with tax."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            "ROUND({{subtotal}} * (1 + {{tax_rate}}), 2)",
            {"subtotal": 156.78, "tax_rate": 0.0825},
        )
        assert round(result, 2) == 169.71


class TestDateFunctions:
    @pytest.mark.asyncio
    async def test_today(self):
        """Test TODAY function returns a number."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate("TODAY()", {})
        assert isinstance(result, (int, float))

    @pytest.mark.asyncio
    async def test_now(self):
        """Test NOW function returns a number."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate("NOW()", {})
        assert isinstance(result, (int, float))

    @pytest.mark.asyncio
    async def test_date(self):
        """Test DATE function."""
        excel_block = ExcelFormula()
        result = await excel_block.evaluate(
            "DATE({{year}}, {{month}}, {{day}})", {"year": 2024, "month": 3, "day": 15}
        )
        assert isinstance(result, (int, float))
        # Convert result to text to verify it's the correct date
        assert result == 45366
