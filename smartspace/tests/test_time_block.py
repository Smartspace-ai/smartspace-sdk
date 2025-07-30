from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from smartspace.blocks.time_block import (
    AddTimeRequest,
    CalculateDifferenceRequest,
    ConvertTimezoneRequest,
    DateTime,
    ExtractComponentsRequest,
    FormatDateRequest,
    GetCurrentRequest,
    ParseDateRequest,
    SubtractTimeRequest,
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
        block.default_format = "%Y-%m-%d"
        return block

    @pytest.fixture
    def test_datetime(self):
        return datetime(2024, 7, 29, 14, 30, 0, tzinfo=ZoneInfo("UTC"))

    @pytest.fixture
    def test_timestamp(self):
        # Create a more predictable timestamp: 2024-07-29 14:30:00 UTC
        dt = datetime(2024, 7, 29, 14, 30, 0, tzinfo=ZoneInfo("UTC"))
        return dt.timestamp()

    # Test get_current operation
    @pytest.mark.asyncio
    async def test_get_current_formatted_default(self, block):
        request = GetCurrentRequest(operation="get_current", format_output=True)
        result = await block.get_current(request)
        assert isinstance(result, str)
        assert len(result) == 19  # YYYY-MM-DD HH:MM:SS format

    @pytest.mark.asyncio
    async def test_get_current_raw_datetime(self, block):
        request = GetCurrentRequest(operation="get_current", format_output=False)
        result = await block.get_current(request)
        assert isinstance(result, datetime)
        assert result.tzinfo is not None

    @pytest.mark.asyncio
    async def test_get_current_custom_timezone(self, block_custom_timezone):
        request = GetCurrentRequest(operation="get_current", format_output=False)
        result = await block_custom_timezone.get_current(request)
        assert isinstance(result, datetime)
        assert str(result.tzinfo) == "America/New_York"

    # Test add_time operation
    @pytest.mark.asyncio
    async def test_add_time_days(self, block, test_datetime):
        request = AddTimeRequest(
            operation="add_time",
            date_input="2024-07-29 14:30:00",
            days=5,
            format_output=True,
        )
        result = await block.add_time(request)
        assert result == "2024-08-03 14:30:00"

    @pytest.mark.asyncio
    async def test_add_time_multiple_units(self, block, test_datetime):
        request = AddTimeRequest(
            operation="add_time",
            date_input="2024-07-29 14:30:00",
            days=1,
            hours=2,
            minutes=30,
            seconds=45,
            format_output=True,
        )
        result = await block.add_time(request)
        assert result == "2024-07-30 17:00:45"

    @pytest.mark.asyncio
    async def test_add_time_timestamp_input(self, block, test_timestamp):
        request = AddTimeRequest(
            operation="add_time", date_input=test_timestamp, days=1, format_output=True
        )
        result = await block.add_time(request)
        assert result == "2024-07-30 14:30:00"

    @pytest.mark.asyncio
    async def test_add_time_raw_output(self, block):
        request = AddTimeRequest(
            operation="add_time",
            date_input="2024-07-29 14:30:00",
            days=1,
            format_output=False,
        )
        result = await block.add_time(request)
        assert isinstance(result, datetime)
        assert result.day == 30

    # Test subtract_time operation
    @pytest.mark.asyncio
    async def test_subtract_time_days(self, block):
        request = SubtractTimeRequest(
            operation="subtract_time",
            date_input="2024-07-29 14:30:00",
            days=5,
            format_output=True,
        )
        result = await block.subtract_time(request)
        assert result == "2024-07-24 14:30:00"

    @pytest.mark.asyncio
    async def test_subtract_time_multiple_units(self, block):
        request = SubtractTimeRequest(
            operation="subtract_time",
            date_input="2024-07-29 14:30:00",
            days=1,
            hours=2,
            minutes=30,
            seconds=15,
            format_output=True,
        )
        result = await block.subtract_time(request)
        assert result == "2024-07-28 11:59:45"

    # Test format_date operation
    @pytest.mark.asyncio
    async def test_format_date_custom_format(self, block):
        request = FormatDateRequest(
            operation="format_date",
            date_input="2024-07-29 14:30:00",
            format_string="%B %d, %Y",
        )
        result = await block.format_date(request)
        assert result == "July 29, 2024"

    @pytest.mark.asyncio
    async def test_format_date_timestamp_input(self, block, test_timestamp):
        request = FormatDateRequest(
            operation="format_date", date_input=test_timestamp, format_string="%Y-%m-%d"
        )
        result = await block.format_date(request)
        assert result == "2024-07-29"

    @pytest.mark.asyncio
    async def test_format_date_invalid_format(self, block):
        # Note: Python's strftime doesn't always raise errors for invalid codes
        # This test verifies that %Q gets passed through literally
        request = FormatDateRequest(
            operation="format_date",
            date_input="2024-07-29 14:30:00",
            format_string="%Q",  # Invalid format code
        )
        result = await block.format_date(request)
        # %Q is not a valid format code, so it should be passed through literally
        assert result == "%Q"

    # Test parse_date operation
    @pytest.mark.asyncio
    async def test_parse_date_automatic_detection(self, block):
        request = ParseDateRequest(
            operation="parse_date", date_string="2024-07-29", format_output=True
        )
        result = await block.parse_date(request)
        assert result == "2024-07-29 00:00:00"

    @pytest.mark.asyncio
    async def test_parse_date_custom_format(self, block):
        request = ParseDateRequest(
            operation="parse_date",
            date_string="29/07/2024",
            input_format="%d/%m/%Y",
            format_output=True,
        )
        result = await block.parse_date(request)
        assert result == "2024-07-29 00:00:00"

    @pytest.mark.asyncio
    async def test_parse_date_iso_format(self, block):
        request = ParseDateRequest(
            operation="parse_date",
            date_string="2024-07-29T14:30:00Z",
            format_output=True,
        )
        result = await block.parse_date(request)
        assert "2024-07-29 14:30:00" in result

    @pytest.mark.asyncio
    async def test_parse_date_invalid_format(self, block):
        request = ParseDateRequest(
            operation="parse_date", date_string="invalid date", format_output=True
        )
        with pytest.raises(BlockError, match="Unable to parse date string"):
            await block.parse_date(request)

    # Test convert_timezone operation
    @pytest.mark.asyncio
    async def test_convert_timezone_utc_to_ny(self, block):
        request = ConvertTimezoneRequest(
            operation="convert_timezone",
            date_input="2024-07-29 14:30:00",
            target_timezone="America/New_York",
            format_output=True,
        )
        result = await block.convert_timezone(request)
        # UTC 14:30 should be NY 10:30 (EDT in July)
        assert result == "2024-07-29 10:30:00"

    @pytest.mark.asyncio
    async def test_convert_timezone_timestamp_input(self, block, test_timestamp):
        request = ConvertTimezoneRequest(
            operation="convert_timezone",
            date_input=test_timestamp,
            target_timezone="Asia/Tokyo",
            format_output=True,
        )
        result = await block.convert_timezone(request)
        # UTC 14:30 should be Tokyo 23:30 (JST is UTC+9)
        assert result == "2024-07-29 23:30:00"

    @pytest.mark.asyncio
    async def test_convert_timezone_raw_output(self, block):
        request = ConvertTimezoneRequest(
            operation="convert_timezone",
            date_input="2024-07-29 14:30:00",
            target_timezone="Europe/London",
            format_output=False,
        )
        result = await block.convert_timezone(request)
        assert isinstance(result, datetime)
        assert str(result.tzinfo) == "Europe/London"

    # Test calculate_difference operation
    @pytest.mark.asyncio
    async def test_calculate_difference_days(self, block):
        request = CalculateDifferenceRequest(
            operation="calculate_difference",
            start_date="2024-07-29 14:30:00",
            end_date="2024-08-03 14:30:00",
            unit="days",
        )
        result = await block.calculate_difference(request)
        assert result == 5

    @pytest.mark.asyncio
    async def test_calculate_difference_hours(self, block):
        request = CalculateDifferenceRequest(
            operation="calculate_difference",
            start_date="2024-07-29 14:30:00",
            end_date="2024-07-29 16:30:00",
            unit="hours",
        )
        result = await block.calculate_difference(request)
        assert result == 2.0

    @pytest.mark.asyncio
    async def test_calculate_difference_negative(self, block):
        request = CalculateDifferenceRequest(
            operation="calculate_difference",
            start_date="2024-07-30 14:30:00",
            end_date="2024-07-29 14:30:00",
            unit="days",
        )
        result = await block.calculate_difference(request)
        assert result == -1

    @pytest.mark.asyncio
    async def test_calculate_difference_timestamp_inputs(self, block, test_timestamp):
        future_timestamp = test_timestamp + 3600  # 1 hour later
        request = CalculateDifferenceRequest(
            operation="calculate_difference",
            start_date=test_timestamp,
            end_date=future_timestamp,
            unit="minutes",
        )
        result = await block.calculate_difference(request)
        assert result == 60.0

    # Test extract_components operation
    @pytest.mark.asyncio
    async def test_extract_components_basic(self, block):
        request = ExtractComponentsRequest(
            operation="extract_components", date_input="2024-07-29 14:30:15"
        )
        result = await block.extract_components(request)
        expected = {
            "year": 2024,
            "month": 7,
            "day": 29,
            "hour": 14,
            "minute": 30,
            "second": 15,
            "weekday": 0,  # Monday
            "iso_weekday": 1,  # Monday
            "day_of_year": 211,  # 29th July is the 211th day of 2024
            "week_of_year": 31,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def test_extract_components_timestamp_input(self, block, test_timestamp):
        request = ExtractComponentsRequest(
            operation="extract_components", date_input=test_timestamp
        )
        result = await block.extract_components(request)
        assert result["year"] == 2024
        assert result["month"] == 7
        assert result["day"] == 29
        assert result["hour"] == 14
        assert result["minute"] == 30

    # Test error handling
    @pytest.mark.asyncio
    async def test_invalid_date_input_type(self, block):
        # Test with an unsupported type that passes Pydantic validation but fails in the method
        request = AddTimeRequest(
            operation="add_time", date_input="not a parseable date string", days=1
        )
        with pytest.raises(BlockError, match="Unable to parse date string"):
            await block.add_time(request)

    @pytest.mark.asyncio
    async def test_invalid_timezone(self, block):
        block.timezone = "Invalid/Timezone"
        request = GetCurrentRequest(operation="get_current")
        with pytest.raises(BlockError, match="Invalid timezone"):
            await block.get_current(request)

    @pytest.mark.asyncio
    async def test_parse_datetime_input_unsupported_string(self, block):
        request = AddTimeRequest(
            operation="add_time", date_input="not a valid date", days=1
        )
        with pytest.raises(BlockError, match="Unable to parse date string"):
            await block.add_time(request)

    # Test edge cases
    @pytest.mark.asyncio
    async def test_leap_year_handling(self, block):
        request = AddTimeRequest(
            operation="add_time",
            date_input="2024-02-28 12:00:00",  # 2024 is a leap year
            days=1,
            format_output=True,
        )
        result = await block.add_time(request)
        assert result == "2024-02-29 12:00:00"  # Should handle leap day correctly

    @pytest.mark.asyncio
    async def test_month_boundary_handling(self, block):
        request = AddTimeRequest(
            operation="add_time",
            date_input="2024-01-31 12:00:00",
            days=31,  # Adding 31 days from Jan 31
            format_output=True,
        )
        result = await block.add_time(request)
        assert "2024-03-02" in result  # Should handle month boundaries correctly

    @pytest.mark.asyncio
    async def test_dst_handling(self, block_custom_timezone):
        # Test during DST transition (this is a complex case)
        # We need to specify the input is in NY timezone for proper conversion
        dt_ny = datetime(2024, 7, 29, 12, 0, 0, tzinfo=ZoneInfo("America/New_York"))
        request = ConvertTimezoneRequest(
            operation="convert_timezone",
            date_input=dt_ny.timestamp(),  # Use timestamp to avoid string parsing issues
            target_timezone="UTC",
            format_output=True,
        )
        result = await block_custom_timezone.convert_timezone(request)
        # Should handle DST correctly (EDT is UTC-4 in summer)
        assert result == "2024-07-29 16:00:00"

    @pytest.mark.asyncio
    async def test_custom_allowed_formats(self, block):
        # Test with a custom allowed format
        block.allowed_formats = ["%d-%m-%Y %H:%M"]
        request = ParseDateRequest(
            operation="parse_date", date_string="29-07-2024 14:30", format_output=True
        )
        result = await block.parse_date(request)
        assert "2024-07-29 14:30:00" in result

    @pytest.mark.asyncio
    async def test_week_calculation_edge_case(self, block):
        # Test week difference calculation
        request = CalculateDifferenceRequest(
            operation="calculate_difference",
            start_date="2024-07-29 00:00:00",  # Monday
            end_date="2024-08-05 00:00:00",  # Next Monday
            unit="weeks",
        )
        result = await block.calculate_difference(request)
        assert result == 1

    @pytest.mark.asyncio
    async def test_microsecond_precision(self, block):
        # Test that microseconds are handled properly using timestamp
        dt_with_microseconds = datetime(
            2024, 7, 29, 14, 30, 0, 123456, tzinfo=ZoneInfo("UTC")
        )
        request = ExtractComponentsRequest(
            operation="extract_components", date_input=dt_with_microseconds.timestamp()
        )
        result = await block.extract_components(request)
        assert result["second"] == 0  # Microseconds don't affect seconds

    @pytest.mark.asyncio
    async def test_year_boundary_week_calculation(self, block):
        # Test week of year calculation at year boundary
        request = ExtractComponentsRequest(
            operation="extract_components", date_input="2024-01-01 00:00:00"
        )
        result = await block.extract_components(request)
        assert "week_of_year" in result
        assert isinstance(result["week_of_year"], int)
