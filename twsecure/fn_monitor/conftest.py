#! /usr/bin/python3.8 Python3.8
import os
from pathlib import Path
import sys


sys.path.append(
    os.path.join(
        Path(os.path.dirname(os.path.abspath(__file__))),
    )
)

import pytest  # NOQA

from tests.local_env_vars import LOCAL_ENV_VARS  # NOQA


@pytest.fixture(scope='session', autouse=True)
def tests_setup_and_teardown():
    # Will be executed before the first test
    old_environ = dict(os.environ)
    os.environ.update(LOCAL_ENV_VARS)

    yield

    # Will be executed after the last test
    os.environ.clear()
    os.environ.update(old_environ)


@pytest.fixture
def dummy_datetime_str():
    return '1970-01-01T00:00:00Z'


@pytest.fixture
def datetime_str_format():
    return '%Y-%m-%dT%H:%M:%SZ'
