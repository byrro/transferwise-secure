#!/usr/bin/python3 Python3
from collections import namedtuple
import datetime
from functools import partial
import hashlib
import json
import logging
import os
from typing import Callable, Dict, List, Optional, Tuple, Union

from get_aws_secret import get_secret
import requests

from datetime_routines import last_24_hours_interval, utc_to_str
import ddb


log = logging.getLogger(os.environ.get('LOGGER_NAME', 'MONITOR_LOGGER'))

LOCAL_ENV = os.environ.get('AWS_SAM_LOCAL') == 'true'
SECRET_ARN = os.environ.get('SECRET_ARN')
API_BASE_URI = 'https://api.transferwise.com'
API_ENDPOINT_SPECS = {
    'get_profiles': {
        'uri': '/v1/profiles',
        'protocol': requests.get,
    },
    'get_accounts': {
        'uri': '/v1/borderless-accounts?profileId={profile_id}',
        'protocol': requests.get,
    },
    'get_statement': {
        'uri': '/v3/profiles/{profile_id}/borderless-accounts/{account_id}/statement.json',  # NOQA
        'protocol': requests.get,
    },
}
DEFAULT_STATEMENT_TYPE = 'COMPACT'
DEFAULT_UNDETERMINED_PAYEE = 'Undetermined'
DEFAULT_TIME_INTERVAL_FUNC = last_24_hours_interval


def get_latest_transactions(
        api_token: str,
        time_interval: Dict[str, datetime.datetime],
) -> Dict[str, str]:
    api = api_endpoints(api_token=api_token)

    return hash_transactions([
        {
            'account': profile['details'].get(
                'firstName',  # Personal account
                profile['details'].get('name', '')  # Business account
            ).split(' ')[0],  # Extract only the first word
            'currency': transaction['amount']['currency'],
            'value': '{:.2f}'.format(abs(transaction['amount']['value'])),
            'payee': get_payee(transaction),
        }
        for profile in api.get_profiles()
        for account in api.get_accounts(profile_id=profile['id'])
        for balance in account['balances']
        for transaction in api.get_statement(
            profile_id=profile['id'],
            account_id=account['id'],
            currency=balance['currency'],
            interval=time_interval,
        )['transactions']
        if account['active'] is True
        if transaction['type'] == 'DEBIT'
    ])


def get_payee(
        transaction: dict,
        default_payee: str = DEFAULT_UNDETERMINED_PAYEE,
        ) -> str:
    details = transaction['details']
    if 'merchant' in details.keys():
        return details['merchant']['name']

    elif 'recipient' in details.keys():
        return details['recipient']['name']

    else:
        return default_payee


def hash_transactions(transactions):
    return [
        {
            'transaction-hash': md5(json.dumps(transaction)),
            'details': transaction,
        }
        for transaction in transactions
    ]


def md5(data: str) -> str:
    return hashlib.md5(data.encode('utf-8')).hexdigest()


def api_request(
        endpoint: str,
        api_token: str,
        base_uri: str = API_BASE_URI,
        endpoint_specs: dict = API_ENDPOINT_SPECS,
        uri_args: Dict[str, str] = {},
        post_data: Dict[str, str] = {},
        query_strs: Dict[str, str] = {},
        ) -> Union[dict, list]:
    http_protocol = endpoint_specs[endpoint]['protocol']
    endpoint_uri = endpoint_specs[endpoint]['uri'].format(**uri_args)
    final_url = base_uri + endpoint_uri

    # log.info(f'## Requesting API URL: {final_url}')
    # log.info(f'.... Query strings: {json.dumps(query_strs)}')
    # log.info(f'.... POST Data: {json.dumps(post_data)}\n')

    response = http_protocol(
        final_url,
        data=post_data,
        params=query_strs,
        headers={'Authorization': f'Bearer {api_token}'},
    )

    # log.info(f'.... Response: {json.dumps(response.json())}')

    return response.json()


def api_endpoints(
        api_token: str,
        base_uri: str = API_BASE_URI,
        endpoint_specs: dict = API_ENDPOINT_SPECS,
        api_request: Callable = api_request,
        statement_type: str = DEFAULT_STATEMENT_TYPE,
        convert_utc_to_str: Callable = utc_to_str,
        ) -> Tuple[Callable]:
    operations = namedtuple('operations', [
        'get_profiles',
        'get_accounts',
        'get_statement',
    ])

    # Pre-set basic api request arguments
    api_request = partial(
        api_request,
        api_token=api_token,
        base_uri=base_uri,
        endpoint_specs=endpoint_specs,
    )

    get_profiles_func = partial(
        get_profiles,
        api_request=api_request,
    )

    get_accounts_func = partial(
        get_accounts,
        api_request=api_request,
    )

    get_statement_func = partial(
        get_statement,
        api_request=api_request,
        statement_type=statement_type,
        convert_utc_to_str=convert_utc_to_str,
    )

    return operations(
        get_profiles=get_profiles_func,
        get_accounts=get_accounts_func,
        get_statement=get_statement_func,
    )


def get_profiles(api_request: Callable) -> List[dict]:
    return api_request(endpoint='get_profiles')


def get_accounts(api_request: Callable, profile_id: str) -> dict:
    return api_request(
        endpoint='get_accounts',
        uri_args={'profile_id': profile_id},
    )


def get_statement(
        api_request: Callable,
        profile_id: str,
        account_id: str,
        currency: str,
        interval: Dict[str, datetime.datetime],
        statement_type: str = DEFAULT_STATEMENT_TYPE,
        convert_utc_to_str: Callable = utc_to_str,
        ) -> dict:
    return api_request(
        endpoint='get_statement',
        uri_args={
            'profile_id': profile_id,
            'account_id': account_id,
        },
        query_strs={
            'currency': currency,
            'intervalStart': convert_utc_to_str(interval['start']),
            'intervalEnd': convert_utc_to_str(interval['end']),
            'type': statement_type,
        },
    )


def run_monitor(
    secret_key: str = SECRET_ARN,
    get_latest_transactions: Callable = get_latest_transactions,
    time_interval_func: Optional[Callable] = DEFAULT_TIME_INTERVAL_FUNC,
) -> dict:
    secret = get_secret(secret_key, load_json=True)
    api_token = secret['api_token']

    tw_transactions = get_latest_transactions(
        api_token=api_token,
        time_interval=time_interval_func(),
    )

    ddb_query = ddb.query()

    # Filter only transactions that aren't already in DynamoDB
    new_transactions = ddb_query.filter_new(transactions=tw_transactions)

    # Insert the new transactions in DynamoDB
    inserted = []
    if len(new_transactions) > 0:
        inserted = ddb_query.insert(transactions=new_transactions)

    return {
        'Transactions Count': {
            'Retrieved from TransferWise': len(tw_transactions),
            'New (unseen) transactions': len(new_transactions),
            'Transactions stored for alerting': len(inserted),
        }
    }


def monitor(run_func: Callable = run_monitor):
    agent = namedtuple('agent', 'run')

    return agent(run=run_func)
