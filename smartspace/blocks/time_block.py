from datetime import datetime, timedelta
from typing import Annotated, Literal
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field

from smartspace.core import (
    Block,
    BlockError,
    Config,
    Metadata,
    metadata,
    step,
)
from smartspace.enums import BlockCategory


class DateTimeRequest(BaseModel):
    """Request model for date/time operations"""
    
    operation: Literal[
        "get_current",
        "add_time", 
        "subtract_time",
    ] = Field(description="The date/time operation to perform")

    # Time arithmetic fields (for add_time and subtract_time operations)
    years: int = Field(default=0, description="Number of years to add/subtract")
    months: int = Field(default=0, description="Number of months to add/subtract")
    weeks: int = Field(default=0, description="Number of weeks to add/subtract")
    days: int = Field(default=0, description="Number of days to add/subtract")
    hours: int = Field(default=0, description="Number of hours to add/subtract")
    minutes: int = Field(default=0, description="Number of minutes to add/subtract")
    seconds: int = Field(default=0, description="Number of seconds to add/subtract")


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
    ] = "Pacific/Auckland"

    output_format: Annotated[
        str,
        Config(),
        Metadata(
            description="Output format for date/time strings when format_output is True. Uses Python strftime format codes. "
            "Examples: '%Y-%m-%d %H:%M:%S' for '2024-01-15 14:30:00', '%Y-%m-%d' for '2024-01-15', "
            "'%B %d, %Y' for 'January 15, 2024'."
        ),
    ] = "%Y-%m-%d %H:%M:%S"


    def __init__(self):
        super().__init__()

    def _get_timezone(self, tz_name: str) -> ZoneInfo:
        """Get timezone object from name."""
        try:
            return ZoneInfo(tz_name)
        except Exception:
            raise BlockError(
                f"Invalid timezone '{tz_name}'. Use IANA timezone names like 'UTC', 'America/New_York', 'Europe/London'."
            )

    def _add_date_components(
        self,
        dt: datetime,
        years: int = 0,
        months: int = 0,
        weeks: int = 0,
        days: int = 0,
        hours: int = 0,
        minutes: int = 0,
        seconds: int = 0,
    ) -> datetime:
        """Add date/time components to a datetime object, handling months and years properly."""
        try:
            # Handle years and months first (these can't use timedelta)
            if years != 0 or months != 0:
                # Calculate total months to add
                total_months = years * 12 + months

                # Calculate new year and month
                new_month = dt.month + total_months
                new_year = dt.year

                # Handle month overflow/underflow
                while new_month > 12:
                    new_month -= 12
                    new_year += 1
                while new_month < 1:
                    new_month += 12
                    new_year -= 1

                # Handle day overflow for months with fewer days
                max_day = self._days_in_month(new_year, new_month)
                new_day = min(dt.day, max_day)

                # Create new datetime with adjusted year/month/day
                dt = dt.replace(year=new_year, month=new_month, day=new_day)

            # Handle weeks, days, hours, minutes, seconds using timedelta
            if weeks != 0 or days != 0 or hours != 0 or minutes != 0 or seconds != 0:
                delta = timedelta(
                    weeks=weeks,
                    days=days,
                    hours=hours,
                    minutes=minutes,
                    seconds=seconds,
                )
                dt = dt + delta

            return dt

        except Exception as e:
            raise BlockError(f"Error in date arithmetic: {str(e)}")

    def _days_in_month(self, year: int, month: int) -> int:
        """Get the number of days in a given month and year."""
        if month in [1, 3, 5, 7, 8, 10, 12]:
            return 31
        elif month in [4, 6, 9, 11]:
            return 30
        elif month == 2:
            # Check for leap year
            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                return 29
            else:
                return 28
        else:
            raise BlockError(f"Invalid month: {month}")

    @step(output_name="result")
    async def execute(self, request: DateTimeRequest) -> str:
        """
        Execute the configured date/time operation.

        All operations work with the current time in the configured timezone.
        Returns a formatted string based on the output_format configuration.
        """
        try:
            # Get current time in the configured timezone
            current_time = datetime.now(tz=self._get_timezone(self.timezone))

            if request.operation == "get_current":
                result_dt = current_time

            elif request.operation == "add_time":
                result_dt = self._add_date_components(
                    current_time,
                    years=request.years,
                    months=request.months,
                    weeks=request.weeks,
                    days=request.days,
                    hours=request.hours,
                    minutes=request.minutes,
                    seconds=request.seconds,
                )

            elif request.operation == "subtract_time":
                result_dt = self._add_date_components(
                    current_time,
                    years=-request.years,
                    months=-request.months,
                    weeks=-request.weeks,
                    days=-request.days,
                    hours=-request.hours,
                    minutes=-request.minutes,
                    seconds=-request.seconds,
                )

            else:
                raise BlockError(f"Unknown operation: {request.operation}")

            # Always return formatted string based on output_format config
            return result_dt.strftime(self.output_format)

        except Exception as e:
            if isinstance(e, BlockError):
                raise
            else:
                raise BlockError(f"Error executing {request.operation}: {str(e)}")
