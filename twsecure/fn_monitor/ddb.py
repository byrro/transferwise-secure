#!/usr/bin/python3 Python3
from collections import namedtuple
from functools import partial
import json
import logging
import os
from typing import Callable, List, NamedTuple, Optional

import botocore

from datetime_routines import calculate_dynamodb_ttl
import simple_dynamodb as simple_ddb


log = logging.getLogger(os.environ.get('LOGGER_NAME', 'MONITOR_LOGGER'))

TRANSACTIONS_TABLE_NAME = os.environ.get('TRANSACTIONS_TABLE_NAME')
DYNAMODB_TTL_IN_DAYS = int(os.environ.get('DYNAMODB_TTL_IN_DAYS', 7))
MAX_NEW_TRANSACTIONS_PER_EXECUTION = int(os.environ.get('MAX_NEW_TRANSACTIONS_PER_EXECUTION', 10))  # NOQA


def filter_new_transactions(
    batch_get: Callable,
    transactions: List[dict],
) -> List[dict]:
    '''Filter a list of transactions and return those not yet in the DB'''
    items = batch_get(
        keys=[
            {'transaction-hash': {'S': t['transaction-hash']}}
            for t in transactions
        ]
    )

    transactions_in_db = [
        item['transaction-hash']['S']
        for item in items
    ]

    return [
        transaction
        for transaction in transactions
        if transaction['transaction-hash'] not in transactions_in_db
    ]


def insert_transactions(
    transactions: List[dict],
    batch_put: Callable,
    max_queue_size: int = MAX_NEW_TRANSACTIONS_PER_EXECUTION,
    ttl_in_days: int = DYNAMODB_TTL_IN_DAYS,
) -> dict:
    ttl = calculate_dynamodb_ttl(delta_period={'days': ttl_in_days})

    return batch_put(
        items=[
            {
                'transaction-hash': {'S': t['transaction-hash']},
                'details': {'S': json.dumps(t['details'])},
                'ttl': {'N': str(ttl)},
            }
            for t in transactions
        ],
        max_queue_size=max_queue_size,
    )


def query_batch_get(
    keys: List[str],
    ddb_api: NamedTuple,
    table_name: str,
) -> List[dict]:
    response = ddb_api.batch_get(keys=keys)
    return response['Responses'][table_name]


def query(
    table_name: str = TRANSACTIONS_TABLE_NAME,
    client: Optional[botocore.client.BaseClient] = None,
    ddb_api: Optional[NamedTuple] = None,
    query_batch_get: Optional[Callable] = query_batch_get,
):
    query = namedtuple('query', 'filter_new insert')

    if not ddb_api:
        ddb_api = simple_ddb.get_table_operations(
            table_name=table_name,
            client=client,
        )

    batch_get = partial(
        query_batch_get,
        table_name=table_name,
        ddb_api=ddb_api,
    )

    filter_new = partial(
        filter_new_transactions,
        batch_get=batch_get,
    )

    insert = partial(
        insert_transactions,
        batch_put=ddb_api.batch_put,
    )

    return query(
        filter_new=filter_new,
        insert=insert,
    )


def get_transactions_operations(table_name: str = TRANSACTIONS_TABLE_NAME):
    return (
        simple_ddb.get_table_operations(table_name=table_name),
        table_name,
    )
