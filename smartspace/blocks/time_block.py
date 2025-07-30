from datetime import datetime, timedelta
from typing import Annotated, Any, Literal, Union
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field

from smartspace.core import (
    Block,
    BlockError,
    Config,
    Metadata,
    Output,
    metadata,
    step,
)
from smartspace.enums import BlockCategory


# Pydantic models for each operation type
class GetCurrentRequest(BaseModel):
    """Get the current date and time"""

    operation: Literal["get_current"] = Field(description="Operation type")
    format_output: bool = Field(
        default=True,
        description="Return formatted string (true) or raw datetime object (false)",
    )


class AddTimeRequest(BaseModel):
    """Add time periods to a date"""

    operation: Literal["add_time"] = Field(description="Operation type")
    date_input: Union[str, int, float] = Field(
        description="Input date as datetime string, Unix timestamp, or formatted date string"
    )
    days: int = Field(default=0, description="Number of days to add")
    hours: int = Field(default=0, description="Number of hours to add")
    minutes: int = Field(default=0, description="Number of minutes to add")
    seconds: int = Field(default=0, description="Number of seconds to add")
    weeks: int = Field(default=0, description="Number of weeks to add")
    format_output: bool = Field(
        default=True,
        description="Return formatted string (true) or raw datetime object (false)",
    )


class SubtractTimeRequest(BaseModel):
    """Subtract time periods from a date"""

    operation: Literal["subtract_time"] = Field(description="Operation type")
    date_input: Union[str, int, float] = Field(
        description="Input date as datetime string, Unix timestamp, or formatted date string"
    )
    days: int = Field(default=0, description="Number of days to subtract")
    hours: int = Field(default=0, description="Number of hours to subtract")
    minutes: int = Field(default=0, description="Number of minutes to subtract")
    seconds: int = Field(default=0, description="Number of seconds to subtract")
    weeks: int = Field(default=0, description="Number of weeks to subtract")
    format_output: bool = Field(
        default=True,
        description="Return formatted string (true) or raw datetime object (false)",
    )


class FormatDateRequest(BaseModel):
    """Format a date with custom strftime patterns"""

    operation: Literal["format_date"] = Field(description="Operation type")
    date_input: Union[str, int, float] = Field(
        description="Input date as datetime string, Unix timestamp, or formatted date string"
    )
    format_string: str = Field(
        description="Format string using Python strftime codes (e.g., '%Y-%m-%d %H:%M:%S', '%B %d, %Y')"
    )


class ParseDateRequest(BaseModel):
    """Parse date strings with flexible format support"""

    operation: Literal["parse_date"] = Field(description="Operation type")
    date_string: str = Field(description="String representation of a date to parse")
    input_format: str = Field(
        default="",
        description="Specific format to use for parsing (optional). If not provided, will try common formats automatically",
    )
    format_output: bool = Field(
        default=True,
        description="Return formatted string (true) or raw datetime object (false)",
    )


class ConvertTimezoneRequest(BaseModel):
    """Convert date/time between different timezones"""

    operation: Literal["convert_timezone"] = Field(description="Operation type")
    date_input: Union[str, int, float] = Field(
        description="Input date as datetime string, Unix timestamp, or formatted date string"
    )
    target_timezone: Literal[
        "UTC",
        "America/New_York",
        "America/Los_Angeles",
        "America/Chicago",
        "America/Denver",
        "America/Toronto",
        "America/Sao_Paulo",
        "Europe/London",
        "Europe/Paris",
        "Europe/Berlin",
        "Europe/Rome",
        "Europe/Madrid",
        "Europe/Amsterdam",
        "Europe/Stockholm",
        "Europe/Zurich",
        "Asia/Tokyo",
        "Asia/Shanghai",
        "Asia/Hong_Kong",
        "Asia/Singapore",
        "Asia/Seoul",
        "Asia/Mumbai",
        "Asia/Dubai",
        "Australia/Sydney",
        "Australia/Melbourne",
        "Pacific/Auckland",
    ] = Field(
        description="Target timezone for conversion. Select from common IANA timezone names"
    )
    format_output: bool = Field(
        default=True,
        description="Return formatted string (true) or raw datetime object (false)",
    )


class CalculateDifferenceRequest(BaseModel):
    """Calculate time differences between two dates"""

    operation: Literal["calculate_difference"] = Field(description="Operation type")
    start_date: Union[str, int, float] = Field(
        description="Start date as datetime string, Unix timestamp, or formatted date string"
    )
    end_date: Union[str, int, float] = Field(
        description="End date as datetime string, Unix timestamp, or formatted date string"
    )
    unit: Literal["days", "hours", "minutes", "seconds", "weeks"] = Field(
        default="days", description="Unit for the difference result"
    )


class ExtractComponentsRequest(BaseModel):
    """Extract date components (year, month, day, etc.)"""

    operation: Literal["extract_components"] = Field(description="Operation type")
    date_input: Union[str, int, float] = Field(
        description="Input date as datetime string, Unix timestamp, or formatted date string"
    )


@metadata(
    category=BlockCategory.FUNCTION,
    description=(
        "Provides comprehensive date and time operations including current time awareness, "
        "date arithmetic, formatting, parsing, timezone conversions, and component extraction. "
        "Supports various input formats (datetime objects, ISO strings, timestamps, formatted strings) "
        "and flexible output formatting for diverse date/time manipulation needs."
    ),
    label="datetime operations, date arithmetic, time formatting, timezone conversion, date parsing",
)
class DateTime(Block):
    """
    A comprehensive date and time operations block that can:
    - Get current date/time with timezone awareness
    - Perform date arithmetic (add/subtract time periods)
    - Format dates in various patterns
    - Parse date strings with flexible input formats
    - Convert between timezones
    - Extract date components (year, month, day, etc.)
    - Calculate time differences and ranges
    """

    timezone: Annotated[
        Literal[
            "UTC",
            "America/New_York",
            "America/Los_Angeles",
            "America/Chicago",
            "America/Denver",
            "America/Toronto",
            "America/Sao_Paulo",
            "Europe/London",
            "Europe/Paris",
            "Europe/Berlin",
            "Europe/Rome",
            "Europe/Madrid",
            "Europe/Amsterdam",
            "Europe/Stockholm",
            "Europe/Zurich",
            "Asia/Tokyo",
            "Asia/Shanghai",
            "Asia/Hong_Kong",
            "Asia/Singapore",
            "Asia/Seoul",
            "Asia/Mumbai",
            "Asia/Dubai",
            "Australia/Sydney",
            "Australia/Melbourne",
            "Pacific/Auckland",
        ],
        Config(),
        Metadata(description="Default timezone for date/time operations."),
    ] = "UTC"

    default_format: Annotated[
        str,
        Config(),
        Metadata(
            description="Default output format for date/time strings. Uses Python strftime format codes. "
            "Examples: '%Y-%m-%d %H:%M:%S' for '2024-01-15 14:30:00', '%Y-%m-%d' for '2024-01-15', "
            "'%B %d, %Y' for 'January 15, 2024'."
        ),
    ] = "%Y-%m-%d %H:%M:%S"

    allowed_formats: Annotated[
        list[str],
        Config(),
        Metadata(
            description="List of accepted input date formats for parsing date strings. "
            "The parser will try each format in order until one succeeds. "
            "Common formats: '%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y %H:%M:%S', etc."
        ),
    ] = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%B %d, %Y",
        "%d %B %Y",
    ]

    # Output declarations
    result: Output[Any]

    def __init__(self):
        super().__init__()

    def _parse_datetime_input(self, date_input: Any) -> datetime:
        """Parse various date input formats to datetime object."""
        if isinstance(date_input, datetime):
            return date_input
        elif isinstance(date_input, (int, float)):
            # Treat as Unix timestamp
            return datetime.fromtimestamp(date_input, tz=ZoneInfo(self.timezone))
        elif isinstance(date_input, str):
            # Try ISO format first
            try:
                return datetime.fromisoformat(date_input.replace("Z", "+00:00"))
            except ValueError:
                pass

            # Try each configured input format
            for fmt in self.allowed_formats:
                try:
                    dt = datetime.strptime(date_input, fmt)
                    # Add timezone if not present
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=ZoneInfo(self.timezone))
                    return dt
                except ValueError:
                    continue

            raise BlockError(
                f"Unable to parse date string '{date_input}' with any of the configured formats: {self.allowed_formats}"
            )
        else:
            raise BlockError(
                f"Unsupported date input type: {type(date_input)}. "
                "Supported types: datetime, int/float (timestamp), str (formatted date)"
            )

    def _get_timezone(self, tz_name: str) -> ZoneInfo:
        """Get timezone object from name."""
        try:
            return ZoneInfo(tz_name)
        except Exception:
            raise BlockError(
                f"Invalid timezone '{tz_name}'. Use IANA timezone names like 'UTC', 'America/New_York', 'Europe/London'."
            )

    @step(output_name="result")
    async def get_current(self, request: GetCurrentRequest) -> Any:
        """
        Get the current date and time in the configured timezone.

        Returns the current date/time either as a formatted string or raw datetime object.
        """
        try:
            current_time = datetime.now(tz=self._get_timezone(self.timezone))
            if request.format_output:
                return current_time.strftime(self.default_format)
            else:
                return current_time
        except Exception as e:
            raise BlockError(f"Error getting current time: {str(e)}")

    @step(output_name="result")
    async def add_time(self, request: AddTimeRequest) -> Any:
        """
        Add time periods (days, hours, minutes, seconds, weeks) to a given date.

        Supports adding multiple time units simultaneously to any input date.
        """
        try:
            dt = self._parse_datetime_input(request.date_input)
            delta = timedelta(
                days=request.days,
                hours=request.hours,
                minutes=request.minutes,
                seconds=request.seconds,
                weeks=request.weeks,
            )
            result_dt = dt + delta
            if request.format_output:
                return result_dt.strftime(self.default_format)
            else:
                return result_dt
        except Exception as e:
            if isinstance(e, BlockError):
                raise
            else:
                raise BlockError(f"Error adding time: {str(e)}")

    @step(output_name="result")
    async def subtract_time(self, request: SubtractTimeRequest) -> Any:
        """
        Subtract time periods (days, hours, minutes, seconds, weeks) from a given date.

        Supports subtracting multiple time units simultaneously from any input date.
        """
        try:
            dt = self._parse_datetime_input(request.date_input)
            delta = timedelta(
                days=request.days,
                hours=request.hours,
                minutes=request.minutes,
                seconds=request.seconds,
                weeks=request.weeks,
            )
            result_dt = dt - delta
            if request.format_output:
                return result_dt.strftime(self.default_format)
            else:
                return result_dt
        except Exception as e:
            if isinstance(e, BlockError):
                raise
            else:
                raise BlockError(f"Error subtracting time: {str(e)}")

    @step(output_name="result")
    async def format_date(self, request: FormatDateRequest) -> str:
        """
        Format a date according to a custom strftime format string.

        Supports all Python strftime format codes for flexible date/time formatting.
        """
        try:
            dt = self._parse_datetime_input(request.date_input)
            format_string = request.format_string or self.default_format
            return dt.strftime(format_string)
        except ValueError as e:
            raise BlockError(f"Invalid format string '{request.format_string}': {e}")
        except Exception as e:
            if isinstance(e, BlockError):
                raise
            else:
                raise BlockError(f"Error formatting date: {str(e)}")

    @step(output_name="result")
    async def parse_date(self, request: ParseDateRequest) -> Any:
        """
        Parse a date string into a datetime object or formatted string.

        Supports custom input formats or automatic detection using configured formats.
        """
        try:
            if request.input_format:
                try:
                    dt = datetime.strptime(request.date_string, request.input_format)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=self._get_timezone(self.timezone))
                except ValueError as e:
                    raise BlockError(
                        f"Unable to parse '{request.date_string}' with format '{request.input_format}': {e}"
                    )
            else:
                dt = self._parse_datetime_input(request.date_string)

            if request.format_output:
                return dt.strftime(self.default_format)
            else:
                return dt
        except Exception as e:
            if isinstance(e, BlockError):
                raise
            else:
                raise BlockError(f"Error parsing date: {str(e)}")

    @step(output_name="result")
    async def convert_timezone(self, request: ConvertTimezoneRequest) -> Any:
        """
        Convert a date/time from one timezone to another.

        Supports all IANA timezone names for accurate timezone conversions.
        """
        try:
            dt = self._parse_datetime_input(request.date_input)
            target_tz = self._get_timezone(request.target_timezone)
            converted_dt = dt.astimezone(target_tz)

            if request.format_output:
                return converted_dt.strftime(self.default_format)
            else:
                return converted_dt
        except Exception as e:
            if isinstance(e, BlockError):
                raise
            else:
                raise BlockError(f"Error converting timezone: {str(e)}")

    @step(output_name="result")
    async def calculate_difference(
        self, request: CalculateDifferenceRequest
    ) -> Union[int, float]:
        """
        Calculate the difference between two dates in the specified unit.

        Returns the numeric difference in days, hours, minutes, seconds, or weeks.
        """
        try:
            start_dt = self._parse_datetime_input(request.start_date)
            end_dt = self._parse_datetime_input(request.end_date)
            delta = end_dt - start_dt

            unit_map = {
                "days": delta.days + delta.seconds / 86400,
                "hours": delta.total_seconds() / 3600,
                "minutes": delta.total_seconds() / 60,
                "seconds": delta.total_seconds(),
                "weeks": (delta.days + delta.seconds / 86400) / 7,
            }

            result = unit_map[request.unit]
            return (
                int(result)
                if request.unit in ["days", "weeks"] and result == int(result)
                else result
            )
        except Exception as e:
            if isinstance(e, BlockError):
                raise
            else:
                raise BlockError(f"Error calculating difference: {str(e)}")

    @step(output_name="result")
    async def extract_components(
        self, request: ExtractComponentsRequest
    ) -> dict[str, int]:
        """
        Extract individual date components (year, month, day, etc.) from a date.

        Returns a dictionary with all date/time components including weekday and day of year.
        """
        try:
            dt = self._parse_datetime_input(request.date_input)
            return {
                "year": dt.year,
                "month": dt.month,
                "day": dt.day,
                "hour": dt.hour,
                "minute": dt.minute,
                "second": dt.second,
                "weekday": dt.weekday(),  # 0=Monday, 6=Sunday
                "iso_weekday": dt.isoweekday(),  # 1=Monday, 7=Sunday
                "day_of_year": dt.timetuple().tm_yday,
                "week_of_year": dt.isocalendar()[1],
            }
        except Exception as e:
            if isinstance(e, BlockError):
                raise
            else:
                raise BlockError(f"Error extracting components: {str(e)}")
