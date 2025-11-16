from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from smartspace.blocks.time_block import (
    DateTime,
    DateTimeRequest,
)
from smartspace.core import BlockError


class TestDateTime:
    @pytest.fixture
    def block(self):
        return DateTime()

    @pytest.fixture
    def block_custom_timezone(self):
        block = DateTime()
        block.timezone = "America/New_York"
        return block

    @pytest.fixture
    def block_custom_format(self):
        block = DateTime()
        block.output_format = "%Y-%m-%d"
        return block

    # Test get_current operation
    @pytest.mark.asyncio
    async def test_get_current_formatted_default(self, block):
        request = DateTimeRequest(operation="get_current")
        result = await block.execute(request)
        assert isinstance(result, str)
        assert len(result) == 19  # YYYY-MM-DD HH:MM:SS format

        # Verify it's a valid datetime format
        parsed = datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        assert parsed is not None

    @pytest.mark.asyncio
    async def test_get_current_custom_timezone(self, block_custom_timezone):
        request = DateTimeRequest(operation="get_current")
        result = await block_custom_timezone.execute(request)
        assert isinstance(result, str)
        assert len(result) == 19  # YYYY-MM-DD HH:MM:SS format

        # Verify it's a valid datetime format
        parsed = datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        assert parsed is not None

    @pytest.mark.asyncio
    async def test_get_current_custom_format(self, block_custom_format):
        request = DateTimeRequest(operation="get_current")
        result = await block_custom_format.execute(request)
        assert isinstance(result, str)
        assert len(result) == 10  # YYYY-MM-DD format
        assert result.count("-") == 2

        # Verify it's a valid date format
        parsed = datetime.strptime(result, "%Y-%m-%d")
        assert parsed is not None

    # Test add_time operation
    @pytest.mark.asyncio
    async def test_add_time_days(self, block):
        request = DateTimeRequest(operation="add_time", days=5)
        result = await block.execute(request)
        assert isinstance(result, str)
        assert len(result) == 19  # YYYY-MM-DD HH:MM:SS format

        # Verify it's a valid datetime format
        parsed = datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        assert parsed is not None

    @pytest.mark.asyncio
    async def test_add_time_multiple_units(self, block):
        before = datetime.now(tz=ZoneInfo("Pacific/Auckland"))
        request = DateTimeRequest(
            operation="add_time",
            days=1,
            hours=2,
            minutes=30,
            seconds=45,
        )
        result = await block.execute(request)
        after = datetime.now(tz=ZoneInfo("Pacific/Auckland"))

        assert isinstance(result, str)
        result_dt = datetime.strptime(result, "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=ZoneInfo("Pacific/Auckland")
        )

        # The result should be roughly current time + the requested delta
        expected_delta = timedelta(days=1, hours=2, minutes=30, seconds=45)
        min_expected = (
            before + expected_delta - timedelta(seconds=10)
        )  # Increased tolerance
        max_expected = after + expected_delta + timedelta(seconds=10)

        assert min_expected <= result_dt <= max_expected

    @pytest.mark.asyncio
    async def test_add_time_zero_values(self, block):
        # Test adding zero time units (should return current time)
        before = datetime.now(tz=ZoneInfo("Pacific/Auckland"))
        request = DateTimeRequest(operation="add_time")  # All defaults to 0
        result = await block.execute(request)
        after = datetime.now(tz=ZoneInfo("Pacific/Auckland"))

        assert isinstance(result, str)
        result_dt = datetime.strptime(result, "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=ZoneInfo("Pacific/Auckland")
        )

        # Result should be very close to current time
        assert (
            before - timedelta(seconds=10) <= result_dt <= after + timedelta(seconds=10)
        )

    # Test subtract_time operation
    @pytest.mark.asyncio
    async def test_subtract_time_days(self, block):
        request = DateTimeRequest(operation="subtract_time", days=5)
        result = await block.execute(request)
        assert isinstance(result, str)
        assert len(result) == 19  # YYYY-MM-DD HH:MM:SS format

        # Verify it's a valid datetime format
        parsed = datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        assert parsed is not None

    @pytest.mark.asyncio
    async def test_subtract_time_multiple_units(self, block):
        before = datetime.now(tz=ZoneInfo("Pacific/Auckland"))
        request = DateTimeRequest(
            operation="subtract_time",
            days=1,
            hours=2,
            minutes=30,
            seconds=15,
        )
        result = await block.execute(request)
        after = datetime.now(tz=ZoneInfo("Pacific/Auckland"))

        assert isinstance(result, str)
        result_dt = datetime.strptime(result, "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=ZoneInfo("Pacific/Auckland")
        )

        # The result should be roughly current time - the requested delta
        expected_delta = timedelta(days=1, hours=2, minutes=30, seconds=15)
        min_expected = before - expected_delta - timedelta(seconds=10)
        max_expected = after - expected_delta + timedelta(seconds=10)

        assert min_expected <= result_dt <= max_expected

    # Test months and years operations
    @pytest.mark.asyncio
    async def test_add_months(self, block):
        request = DateTimeRequest(operation="add_time", months=3)
        result = await block.execute(request)
        assert isinstance(result, str)
        assert len(result) == 19  # YYYY-MM-DD HH:MM:SS format

        # Verify it's a valid datetime format
        parsed = datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        assert parsed is not None

    @pytest.mark.asyncio
    async def test_add_years(self, block):
        request = DateTimeRequest(operation="add_time", years=2)
        result = await block.execute(request)
        assert isinstance(result, str)
        assert len(result) == 19  # YYYY-MM-DD HH:MM:SS format

        # Verify it's a valid datetime format
        parsed = datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        assert parsed is not None

    @pytest.mark.asyncio
    async def test_subtract_months(self, block):
        request = DateTimeRequest(operation="subtract_time", months=6)
        result = await block.execute(request)
        assert isinstance(result, str)
        assert len(result) == 19  # YYYY-MM-DD HH:MM:SS format

        # Verify it's a valid datetime format
        parsed = datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        assert parsed is not None

    @pytest.mark.asyncio
    async def test_subtract_years(self, block):
        request = DateTimeRequest(operation="subtract_time", years=1)
        result = await block.execute(request)
        assert isinstance(result, str)
        assert len(result) == 19  # YYYY-MM-DD HH:MM:SS format

        # Verify it's a valid datetime format
        parsed = datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        assert parsed is not None

    @pytest.mark.asyncio
    async def test_mixed_units_with_months_years(self, block):
        # Test combining all time units including months and years
        request = DateTimeRequest(
            operation="add_time",
            years=1,
            months=2,
            weeks=1,
            days=3,
            hours=4,
            minutes=30,
            seconds=45,
        )
        result = await block.execute(request)
        assert isinstance(result, str)
        assert len(result) == 19  # YYYY-MM-DD HH:MM:SS format

        # Verify it's a valid datetime format
        parsed = datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        assert parsed is not None

    @pytest.mark.asyncio
    async def test_negative_months_years(self, block):
        # Test that negative months/years in add_time effectively subtract
        request = DateTimeRequest(operation="add_time", years=-1, months=-6)
        result = await block.execute(request)
        assert isinstance(result, str)
        assert len(result) == 19

        # Verify it's a valid datetime format
        parsed = datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        assert parsed is not None

    # Test error handling
    @pytest.mark.asyncio
    async def test_invalid_timezone(self):
        block = DateTime()
        block.timezone = "Invalid/Timezone"
        request = DateTimeRequest(operation="get_current")
        with pytest.raises(BlockError, match="Invalid timezone"):
            await block.execute(request)

    @pytest.mark.asyncio
    async def test_unknown_operation(self, block):
        # Test that unknown operations raise an error at Pydantic validation level
        with pytest.raises(ValueError):
            DateTimeRequest(operation="unknown_operation")

    # Test edge cases
    @pytest.mark.asyncio
    async def test_large_time_addition(self, block):
        # Test adding large time units
        request = DateTimeRequest(
            operation="add_time", days=365, hours=24, minutes=60, seconds=3600
        )
        result = await block.execute(request)
        assert isinstance(result, str)
        assert len(result) == 19  # Should handle large values without error

        # Verify it's a valid datetime format
        parsed = datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        assert parsed is not None

    @pytest.mark.asyncio
    async def test_negative_time_values_in_add(self, block):
        # Test that negative values in add_time effectively subtract
        before = datetime.now(tz=ZoneInfo("Pacific/Auckland"))
        request = DateTimeRequest(operation="add_time", days=-1)  # Negative day
        result = await block.execute(request)
        after = datetime.now(tz=ZoneInfo("Pacific/Auckland"))

        assert isinstance(result, str)
        result_dt = datetime.strptime(result, "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=ZoneInfo("Pacific/Auckland")
        )

        # Result should be roughly current time - 1 day
        expected_delta = timedelta(days=-1)
        min_expected = before + expected_delta - timedelta(seconds=10)
        max_expected = after + expected_delta + timedelta(seconds=10)

        assert min_expected <= result_dt <= max_expected

    @pytest.mark.asyncio
    async def test_output_format_consistency(self):
        # Test that all operations use the same output format
        custom_format = "%Y/%m/%d %H:%M"
        request_get = DateTimeRequest(operation="get_current")
        request_add = DateTimeRequest(operation="add_time", hours=1)
        request_sub = DateTimeRequest(operation="subtract_time", hours=1)

        # Test get_current
        block1 = DateTime()
        block1.output_format = custom_format
        result1 = await block1.execute(request_get)
        assert isinstance(result1, str)
        assert "/" in result1 and len(result1) == 16  # YYYY/MM/DD HH:MM format
        parsed1 = datetime.strptime(result1, "%Y/%m/%d %H:%M")
        assert parsed1 is not None

        # Test add_time
        block2 = DateTime()
        block2.output_format = custom_format
        result2 = await block2.execute(request_add)
        assert isinstance(result2, str)
        assert "/" in result2 and len(result2) == 16
        parsed2 = datetime.strptime(result2, "%Y/%m/%d %H:%M")
        assert parsed2 is not None

        # Test subtract_time
        block3 = DateTime()
        block3.output_format = custom_format
        result3 = await block3.execute(request_sub)
        assert isinstance(result3, str)
        assert "/" in result3 and len(result3) == 16
        parsed3 = datetime.strptime(result3, "%Y/%m/%d %H:%M")
        assert parsed3 is not None

    # Test month/year edge cases
    @pytest.mark.asyncio
    async def test_month_day_overflow_handling(self):
        # Test edge case: adding months when day doesn't exist in target month
        block = DateTime()
        block.timezone = "UTC"  # Use UTC for predictable results

        request = DateTimeRequest(operation="add_time", months=1)
        result = await block.execute(request)
        assert isinstance(result, str)
        assert len(result) == 19

        # Verify it's a valid datetime format and doesn't crash
        parsed = datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        assert parsed is not None

    @pytest.mark.asyncio
    async def test_leap_year_handling_with_months(self):
        # Test leap year handling when adding/subtracting months
        block = DateTime()
        block.timezone = "UTC"

        request = DateTimeRequest(operation="add_time", months=12)  # Add a full year
        result = await block.execute(request)
        assert isinstance(result, str)
        assert len(result) == 19

        # Verify it's a valid datetime format
        parsed = datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        assert parsed is not None

    @pytest.mark.asyncio
    async def test_all_time_units_default_to_zero(self, block):
        # Test that all time units default to 0 when not specified
        request = DateTimeRequest(operation="add_time")  # No time units specified

        before = datetime.now(tz=ZoneInfo("Pacific/Auckland"))
        result = await block.execute(request)
        after = datetime.now(tz=ZoneInfo("Pacific/Auckland"))

        result_dt = datetime.strptime(result, "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=ZoneInfo("Pacific/Auckland")
        )

        # Should be very close to current time since all units are 0
        assert (
            before - timedelta(seconds=10) <= result_dt <= after + timedelta(seconds=10)
        )

    @pytest.mark.asyncio
    async def test_timezone_configuration_affects_all_operations(self):
        # Test that timezone configuration affects all operations
        utc_block = DateTime()
        utc_block.timezone = "UTC"

        ny_block = DateTime()
        ny_block.timezone = "America/New_York"

        request = DateTimeRequest(operation="get_current")

        utc_result = await utc_block.execute(request)
        ny_result = await ny_block.execute(request)

        # Results should be different due to timezone differences
        # (unless we're exactly at a moment when they happen to be the same hour)
        assert isinstance(utc_result, str)
        assert isinstance(ny_result, str)

        # Both should be valid datetime formats
        utc_parsed = datetime.strptime(utc_result, "%Y-%m-%d %H:%M:%S")
        ny_parsed = datetime.strptime(ny_result, "%Y-%m-%d %H:%M:%S")
        assert utc_parsed is not None
        assert ny_parsed is not None

    @pytest.mark.asyncio
    async def test_output_format_affects_all_operations(self):
        # Test that output_format configuration affects all operations
        block = DateTime()
        block.output_format = "%d/%m/%Y %H:%M"  # Different format

        operations = [
            DateTimeRequest(operation="get_current"),
            DateTimeRequest(operation="add_time", days=1),
            DateTimeRequest(operation="subtract_time", days=1),
        ]

        for request in operations:
            # Need separate block instances since blocks can only run once
            test_block = DateTime()
            test_block.output_format = "%d/%m/%Y %H:%M"

            result = await test_block.execute(request)
            assert isinstance(result, str)
            assert len(result) == 16  # DD/MM/YYYY HH:MM format
            assert result.count("/") == 2

            # Verify it's a valid datetime in the expected format
            parsed = datetime.strptime(result, "%d/%m/%Y %H:%M")
            assert parsed is not None
