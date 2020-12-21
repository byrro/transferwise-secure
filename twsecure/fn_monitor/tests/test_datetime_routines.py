import copy
import datetime
from unittest import mock

import pytest

from datetime_routines import (
    calculate_dynamodb_ttl,
    last_24_hours_interval,
    last_delta_interval,
    utc_to_str,
)


@pytest.fixture
def dummy_datetime_params():
    return {
        'year': 2020,
        'month': 6,
        'day': 15,
        'hour': 12,
        'minute': 30,
        'second': 30,
        'microsecond': 100000,
    }


@pytest.fixture
def dummy_datetime(dummy_datetime_params):
    params = copy.deepcopy(dummy_datetime_params)
    return datetime.datetime(**params)


@pytest.fixture
def dummy_timestamp():
    return 1592224230


@pytest.fixture
def dummy_datetime_one_hour_before(dummy_datetime_params):
    params = copy.deepcopy(dummy_datetime_params)
    params['hour'] -= 1
    return datetime.datetime(**params)


@pytest.fixture
def dummy_datetime_two_days_before(dummy_datetime_params):
    params = copy.deepcopy(dummy_datetime_params)
    params['day'] -= 2
    return datetime.datetime(**params)


@pytest.fixture
def dummy_datetime_fifteen_minutes_before(dummy_datetime_params):
    params = copy.deepcopy(dummy_datetime_params)
    params['minute'] -= 15
    return datetime.datetime(**params)


@pytest.fixture
def dummy_datetime_two_days_after(dummy_datetime_params):
    params = copy.deepcopy(dummy_datetime_params)
    params['day'] += 2


@pytest.fixture
def dummy_datetime_fifteen_minutes_after(dummy_datetime_params):
    params = copy.deepcopy(dummy_datetime_params)
    params['minute'] += 15


@pytest.fixture
def dummy_datetime_one_hour_after(dummy_datetime_params):
    params = copy.deepcopy(dummy_datetime_params)
    params['hour'] += 1


def test_utc_to_str(dummy_datetime_str, datetime_str_format):
    mock_datetime = mock.Mock()
    mock_datetime.strftime = mock.Mock(return_value=dummy_datetime_str)

    response = utc_to_str(
        dt=mock_datetime,
        datetime_str_format=datetime_str_format,
    )

    assert response == dummy_datetime_str

    mock_datetime.strftime.assert_called_with(datetime_str_format)


@mock.patch('datetime_routines.last_delta_interval')
def test_last_24_hours_interval(last_delta_interval):
    dummy_interval = {
        'start': datetime.datetime.now(),
        'end': datetime.datetime.now(),
    }
    last_delta_interval.return_value = dummy_interval
    time_interval = last_24_hours_interval(timezone=datetime.timezone.utc)

    assert time_interval == dummy_interval

    last_delta_interval.assert_called_with(
        delta_period={'hours': 24},
        timezone=datetime.timezone.utc,
    )


@mock.patch('datetime.datetime')
def test_last_delta_interval(
        datetime_mock,
        dummy_datetime,
        dummy_datetime_fifteen_minutes_before,
        dummy_datetime_one_hour_before,
        dummy_datetime_two_days_before,
        ):
    # Omit 'now' arg, force generating a 'datetime.now' inside the function
    datetime_mock.now = mock.Mock(return_value=dummy_datetime)

    # Test one hour before
    interval = last_delta_interval(
        delta_period={'hours': 1},
        timezone=datetime.timezone.utc,
    )
    assert interval['end'] == dummy_datetime
    assert interval['start'] == dummy_datetime_one_hour_before

    # Test fifteen minutes before
    interval = last_delta_interval(
        delta_period={'minutes': 15},
        timezone=datetime.timezone.utc,
    )
    assert interval['end'] == dummy_datetime
    assert interval['start'] == dummy_datetime_fifteen_minutes_before

    # Test two days before
    interval = last_delta_interval(
        delta_period={'days': 2},
        timezone=datetime.timezone.utc,
    )

    assert interval['end'] == dummy_datetime
    assert interval['start'] == dummy_datetime_two_days_before


@mock.patch('datetime.datetime')
def test_calculate_dynamodb_ttl(
    datetime,
    dummy_datetime,
    dummy_datetime_one_hour_after,
    dummy_datetime_two_days_after,
    dummy_datetime_fifteen_minutes_after,
    dummy_timestamp,
):
    datetime.utcnow = mock.Mock(return_value=dummy_datetime)

    ttl = calculate_dynamodb_ttl(delta_period={'hours': 1})
    assert type(ttl) is int
    assert ttl == dummy_timestamp + 60*60

    ttl = calculate_dynamodb_ttl(delta_period={'minutes': 15})
    assert type(ttl) is int
    assert ttl == dummy_timestamp + 15*60

    ttl = calculate_dynamodb_ttl(delta_period={'days': 2})
    assert type(ttl) is int
    assert ttl == dummy_timestamp + 2*24*60*60
