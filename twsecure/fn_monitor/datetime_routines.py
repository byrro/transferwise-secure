#!/usr/bin/python3 Python3
import calendar
import datetime
from typing import Dict


DEFAULT_DATETIME_STR_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


def utc_to_str(
        dt: datetime.datetime,
        datetime_str_format: str = DEFAULT_DATETIME_STR_FORMAT,
        ) -> str:
    return dt.strftime(datetime_str_format)


def last_delta_interval(
        delta_period: dict,
        now: datetime.datetime = None,
        timezone: datetime.tzinfo = datetime.timezone.utc,
        ) -> Dict[str, datetime.datetime]:
    if not now:
        now = datetime.datetime.now(timezone)

    return {
        'start': now - datetime.timedelta(**delta_period),
        'end': now,
    }


def last_24_hours_interval(
        timezone: datetime.tzinfo = datetime.timezone.utc,
        ) -> Dict[str, datetime.datetime]:
    return last_delta_interval(delta_period={'hours': 24}, timezone=timezone)


def calculate_dynamodb_ttl(delta_period: Dict[str, int]) -> int:
    future = datetime.datetime.utcnow() + datetime.timedelta(**delta_period)
    return calendar.timegm(future.timetuple())
