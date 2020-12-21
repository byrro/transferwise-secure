#!/usr/bin/python3 Python3
import queue
import uuid

import pytest

from retry_queue import (
    RetryQueueItem,
    RetryLimitQueue,
    TooManyRetriesException,
)


def test_uuid_generator():
    item = {'hello': 'world'}
    expected_uuid = str(uuid.uuid5(uuid.NAMESPACE_X500, str(item)))
    actual = RetryQueueItem(item)

    assert expected_uuid == actual.uuid


def test_put_and_get_item():
    max_retries = 3
    test_queue = RetryLimitQueue(max_retries=max_retries)
    item = {'hello': 'world'}

    test_queue.put_nowait(item)
    item = test_queue.get_nowait()

    assert item == item


def test_item_retry_count():
    max_retries = 5
    test_queue = RetryLimitQueue(max_retries=max_retries)
    item = {'hello': 'world'}

    for i in range(1, max_retries):
        test_queue.put_nowait(item)
        test_queue.get_nowait()
        assert test_queue.item_retry_count(item) == i


def test_too_many_retries_exception():
    max_retries = 3
    test_queue = RetryLimitQueue(max_retries=max_retries)
    item = {'hello': 'world'}

    with pytest.raises(TooManyRetriesException) as exc_info:
        for i in range(0, max_retries+1):
            test_queue.put_nowait(item)
            test_queue.get_nowait()

        assert exc_info.retry_count == max_retries

    assert test_queue.item_retry_count(item) == max_retries

    # Make sure the item is really not there
    with pytest.raises(queue.Empty):
        test_queue.get_nowait()


def test_retry_empty_exception():
    test_range_size = 3

    test_queue = RetryLimitQueue(max_retries=1)

    # Test with an empty queue
    with pytest.raises(queue.Empty):
        test_queue.get_nowait()

    # Fill the queue with some items
    for i in range(0, test_range_size):
        test_queue.put_nowait(i)

    # Retrieve all items
    for i in range(0, test_range_size):
        test_queue.get_nowait()

    with pytest.raises(queue.Empty):
        test_queue.get_nowait()


def test_retry_full_exception():
    max_size = 3
    test_queue = RetryLimitQueue(max_retries=1, maxsize=max_size)

    # Test that exception is not raised
    try:
        test_queue.put_nowait('whatever')
    except queue.Full:
        pytest.fail('Caught an unexpected queue.Full error')

    # Fill the queue with more items than it can handle
    with pytest.raises(queue.Full):
        for i in range(0, max_size + 1):
            test_queue.put_nowait(i)


def test_inexistent_item_exception():
    test_queue = RetryLimitQueue(max_retries=1)

    dummy_item = {'hello': 'world'}
    inexistent_item = {'hello': 'worldz'}

    test_queue.put_nowait(dummy_item)

    with pytest.raises(LookupError):
        test_queue.item_retry_count(inexistent_item)
