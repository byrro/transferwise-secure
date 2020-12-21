#!/usr/bin/python3 Python3
import copy
from functools import partial
import json
import os
from unittest import mock

import pytest

import ddb
import simple_dynamodb as simple_ddb


@pytest.fixture
def sample_transactions_size():
    return 10


@pytest.fixture
def sample_transactions(sample_transactions_size):
    return [
        {
            'transaction-hash': f'hash-{str(i)}',
            'details': {'i': i},
        }
        for i in range(0, sample_transactions_size)
    ]


@pytest.fixture
def sample_transaction_ddb_items(sample_transactions):
    return [
        {'transaction-hash': {'S': t['transaction-hash']}}
        for t in sample_transactions
    ]


def test_query_batch_get():
    keys = ['A', 'B', 'C']
    table_name = 'DummyTable'
    items = [{'a': 'A'}, {'b': 'B'}]
    batch_get_response = {'Responses': {table_name: items}}
    ddb_api = mock.Mock()
    ddb_api.batch_get = mock.Mock(return_value=batch_get_response)

    response = ddb.query_batch_get(keys, ddb_api, table_name)

    assert response == items
    ddb_api.batch_get.assert_called_with(keys=keys)


@mock.patch('boto3.client')
def test_query_default_args(boto3_client):
    query = ddb.query()

    assert hasattr(query, 'filter_new')
    assert hasattr(query, 'insert')

    assert isinstance(query.filter_new, partial)
    assert query.filter_new.func == ddb.filter_new_transactions

    batch_get = query.filter_new.keywords.get('batch_get')
    assert batch_get is not None
    assert isinstance(batch_get, partial)
    assert batch_get.func == ddb.query_batch_get
    assert batch_get.keywords.get('table_name') == ddb.TRANSACTIONS_TABLE_NAME
    assert isinstance(batch_get.keywords.get('ddb_api'), simple_ddb.table_operations)  # NOQA

    assert isinstance(query.insert, partial)
    assert query.insert.func == ddb.insert_transactions

    assert query.insert.keywords.get('table_name') == ddb.TRANSACTIONS_TABLE_NAME  # NOQA
    assert 'batch_put' in query.insert.keywords


@mock.patch('boto3.client')
def test_get_transactions_operations(boto3_client):
    assert os.environ.get('LOCAL_ENV_VARS_LOADED') == 'true'

    dummy_table = 'dummy_table'
    response = ddb.get_transactions_operations(table_name=dummy_table)

    assert type(response) == tuple
    assert len(response) == 2
    assert isinstance(response[0], simple_ddb.table_operations)
    assert response[1] == dummy_table


def test_filter_new_transactions(
    sample_transactions,
    sample_transaction_ddb_items,
):
    sample_ddb_items = copy.deepcopy(sample_transaction_ddb_items)

    # Test when all transactions are already in DDB
    batch_get = mock.Mock(return_value=sample_ddb_items)

    new_transactions = ddb.filter_new_transactions(
        transactions=sample_transactions,
        batch_get=batch_get,
    )

    batch_get.assert_called_once_with(
        keys=[
            {'transaction-hash': {'S': t['transaction-hash']}}
            for t in sample_transactions
        ]
    )

    # Since all transactions are in DDB, the 'filter_new' should return none
    assert type(new_transactions) is list
    assert len(new_transactions) == 0

    # Test when a few transactions are not in DB
    removed_hashes = []
    removal_count = 2
    for i in range(0, removal_count):
        removed_hashes.append(sample_ddb_items[i]['transaction-hash']['S'])
        del sample_ddb_items[i]

    not_removed_hashes = [t['transaction-hash']['S'] for t in sample_ddb_items]

    batch_get = mock.Mock(return_value=sample_ddb_items)

    new_transactions = ddb.filter_new_transactions(
        transactions=sample_transactions,
        batch_get=batch_get,
    )

    new_hashes = [t['transaction-hash'] for t in new_transactions]

    assert len(new_transactions) == removal_count

    for hash_ in removed_hashes:
        assert hash_ in new_hashes

    for hash_ in not_removed_hashes:
        assert hash_ not in new_hashes

    # Test when none of the transactions are in DDB
    batch_get = mock.Mock(return_value=[])

    new_transactions = ddb.filter_new_transactions(
        transactions=sample_transactions,
        batch_get=batch_get,
    )

    assert len(new_transactions) == len(sample_transactions)


@mock.patch('ddb.calculate_dynamodb_ttl')
def test_insert_transactions(calculate_dynamodb_ttl, sample_transactions):
    ttl_in_days = 7
    ttl_timestamp = 1234567890
    calculate_dynamodb_ttl.return_value = ttl_timestamp

    batch_put_response = mock.Mock()
    batch_put = mock.Mock(return_value=batch_put_response)

    response = ddb.insert_transactions(
        transactions=sample_transactions,
        batch_put=batch_put,
        max_queue_size=10,
        ttl_in_days=ttl_in_days,
    )

    assert response == batch_put_response

    calculate_dynamodb_ttl.assert_called_with(
        delta_period={'days': ttl_in_days},
    )

    batch_put.assert_called_with(
        items=[
            {
                'transaction-hash': {'S': t['transaction-hash']},
                'details': {'S': json.dumps(t['details'])},
                'ttl': {'N': str(ttl_timestamp)},
            }
            for t in sample_transactions
        ],
        max_queue_size=ddb.MAX_NEW_TRANSACTIONS_PER_EXECUTION,
    )
