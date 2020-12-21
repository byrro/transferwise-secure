import copy
from functools import partial
import json
import random
from unittest import mock

import pytest

from transferwise import (
    api_endpoints,
    api_request,
    get_accounts,
    get_payee,
    get_profiles,
    get_statement,
    hash_transactions,
    md5,
    monitor,
    run_monitor,
)


@pytest.fixture
def dummy_merchant():
    return 'Dummy Merchant'


@pytest.fixture
def dummy_recipient():
    return 'Dummy Recipient'


@pytest.fixture
def transaction_merchant(dummy_merchant):
    return {
        "type": "DEBIT",
        "date": "2020-12-01T17:05:44.286576Z",
        "amount": {
            "value": -10,
            "currency": "USD",
        },
        "totalFees": {
            "value": 0,
            "currency": "USD",
        },
        "details": {
            "type": "CARD",
            "description": f"Card transaction of 10.00 USD issued by {dummy_merchant}",  # NOQA
            "amount": {
                "value": 10,
                "currency": "USD",
            },
            "category": "Computer Network/Information Ser",
            "merchant": {
                "name": dummy_merchant,
                "firstLine": None,
                "postCode": "12345",
                "city": None,
                "state": None,
                "country": "US",
                "category": "Computer Network/Information Ser",
            },
        },
        "exchangeDetails": None,
        "runningBalance": {
            "value": 123.45,
            "currency": "USD"
        },
        "referenceNumber": "CARD-12345678",
    }


@pytest.fixture
def transaction_recipient(dummy_recipient):
    return {
        "type": "DEBIT",
        "date": "2020-12-15T03:52:28.683589Z",
        "amount": {
            "value": -150.00,
            "currency": "USD",
        },
        "totalFees": {
            "value": 1.49,
            "currency": "USD",
        },
        "details": {
            "type": "TRANSFER",
            "description": f"Sent money to {dummy_recipient}",
            "recipient": {
                "name": dummy_recipient,
                "bankAccount": "1*******9",
            },
            "paymentReference": "",
        },
        "exchangeDetails": None,
        "runningBalance": {
            "value": 123.45,
            "currency": "USD",
        },
        "referenceNumber": "TRANSFER-123456789",
    }


@pytest.fixture
def transaction_no_payee(transaction_merchant):
    transaction = copy.deepcopy(transaction_merchant)
    del transaction['details']['merchant']
    return transaction


@pytest.fixture
def lastest_transactions_count():
    return 10


@pytest.fixture
def dummy_latest_transactions(
    dummy_merchant,
    dummy_recipient,
    lastest_transactions_count,
):
    payees = [dummy_merchant, dummy_recipient]
    return [
        {
            'account': 'Dummy',
            'currency': 'XYZ',
            'value': float(i * -1),
            'payee': random.choice(payees),
        }
        for i in range(1, lastest_transactions_count)
    ]


def test_get_payee(
        dummy_merchant,
        dummy_recipient,
        transaction_merchant,
        transaction_recipient,
        transaction_no_payee,
        ):
    payee = get_payee(transaction_merchant)
    assert type(payee) is str
    assert payee == dummy_merchant

    payee = get_payee(transaction_recipient)
    assert type(payee) is str
    assert payee == dummy_recipient

    default_payee = 'dummy'
    payee = get_payee(transaction_no_payee, default_payee=default_payee)
    assert type(payee) is str
    assert payee == default_payee


def test_md5():
    test_set = {
        'testing 123': '29628f6790da2e7daa6f40ab933e05d9',
        'xyz': 'd16fb36f0911f878998c136191af705e',
        json.dumps({'hello': 'world'}): '49dfdd54b01cbcd2d2ab5e9e5ee6b9b9',
    }

    for value, expected_hash in test_set.items():
        hash_ = md5(value)
        assert hash_ == expected_hash


def test_hash_transactions(transaction_merchant, transaction_recipient):
    expected_hashes = {
        str(transaction_merchant): '373256bff664e73b5051d63108a88b8e',
        str(transaction_recipient): 'e327997743cbda4ab117d4254371ea9e',
    }

    hashed = hash_transactions([transaction_merchant, transaction_recipient])

    for item in hashed:
        transaction_str = str(item['details'])
        hashed_value = item['transaction-hash']

        assert expected_hashes[transaction_str] == hashed_value


def test_api_endpoints():
    api = api_endpoints(api_token='ABC123')

    assert hasattr(api, 'get_profiles')
    assert hasattr(api, 'get_accounts')
    assert hasattr(api, 'get_statement')


def test_api_request():
    dummy_response = {'status': '200', 'hello': 'world'}

    protocol_response = mock.Mock()
    protocol_response.json = mock.Mock(return_value=dummy_response)
    http_protocol = mock.Mock(return_value=protocol_response)

    api_token = 'TOKEN123'
    base_uri = 'https://dummyhost:123'
    endpoint_uri = '/v1/dummy'
    final_url = base_uri + endpoint_uri

    endpoint_specs = {
        'dummy_endpoint': {
            'uri': endpoint_uri,
            'protocol': http_protocol,
        }
    }

    dummy_api_request = partial(
        api_request,
        endpoint='dummy_endpoint',
        api_token=api_token,
        base_uri=base_uri,
        endpoint_specs=endpoint_specs,
    )

    # Test with default args
    response = dummy_api_request()
    http_protocol.assert_called_with(
        final_url,
        data={},
        params={},
        headers={'Authorization': f'Bearer {api_token}'},
    )
    protocol_response.json.assert_called()
    assert response == dummy_response

    # Test with custom POST data
    response = dummy_api_request(post_data={'foo': 'bar'})
    http_protocol.assert_called_with(
        final_url,
        data={'foo': 'bar'},
        params={},
        headers={'Authorization': f'Bearer {api_token}'},
    )

    # Test with URI args
    uri_args = {'foo': 'bar'}
    custom_uri = '?foo={foo}'
    final_url = base_uri + endpoint_uri + custom_uri.format(**uri_args)
    new_endpoint_specs = {
        'dummy_endpoint': {
            'uri': endpoint_uri + custom_uri,
            'protocol': http_protocol,
        }
    }
    dummy_api_request = partial(
        api_request,
        endpoint='dummy_endpoint',
        api_token=api_token,
        base_uri=base_uri,
        endpoint_specs=new_endpoint_specs,
    )
    response = dummy_api_request(uri_args=uri_args)
    http_protocol.assert_called_with(
        final_url,
        data={},
        params={},
        headers={'Authorization': f'Bearer {api_token}'},
    )


def test_get_profiles():
    api_request = mock.Mock(return_value='test_get_profiles')

    response = get_profiles(api_request=api_request)

    assert response == 'test_get_profiles'
    api_request.assert_called_with(endpoint='get_profiles')


def test_get_accounts():
    profile_id = 'abc123'

    api_request = mock.Mock(return_value='test_get_accounts')

    response = get_accounts(api_request=api_request, profile_id=profile_id)

    assert response == 'test_get_accounts'
    api_request.assert_called_with(
        endpoint='get_accounts',
        uri_args={'profile_id': profile_id},
    )


def test_get_statement(dummy_datetime_str):
    mock_interval = {
        'start': mock.Mock(),
        'end': mock.Mock(),
    }
    convert_utc_to_str = mock.Mock(return_value=dummy_datetime_str)

    profile_id = 'PROFILE-123'
    account_id = 'ACCOUNT-123'
    currency = '$XYZ'
    interval = mock.NonCallableMagicMock(spec=dict)
    statement_type = 'DUMMY-STATEMENT-TYPE'

    interval.__getitem__ = lambda self, key: mock_interval.get(key, 'unknown')

    api_request = mock.Mock(return_value='test_get_statement')

    response = get_statement(
        api_request=api_request,
        profile_id=profile_id,
        account_id=account_id,
        currency=currency,
        interval=interval,
        statement_type=statement_type,
        convert_utc_to_str=convert_utc_to_str,
    )

    assert response == 'test_get_statement'
    assert convert_utc_to_str.call_count == 2
    convert_utc_to_str.assert_has_calls([
        mock.call(mock_interval['start']),
        mock.call(mock_interval['end']),
    ])
    api_request.assert_called_with(
        endpoint='get_statement',
        uri_args={'profile_id': profile_id, 'account_id': account_id},
        query_strs={
            'currency': currency,
            'intervalStart': dummy_datetime_str,
            'intervalEnd': dummy_datetime_str,
            'type': statement_type,
        },
    )


def test_monitor():
    run_func = mock.Mock()

    agent = monitor(run_func=run_func)

    assert hasattr(agent, 'run')
    assert agent.run == run_func

    agent = monitor()

    assert agent.run == run_monitor


@mock.patch('transferwise.get_secret')
@mock.patch('transferwise.ddb')
def test_run_monitor(
    ddb_mock,
    get_secret,
    dummy_latest_transactions,
    lastest_transactions_count,
):
    secret_key = 'DUMMY_SECRET'
    api_token = 'dummy-token'
    get_secret.return_value = {'api_token': api_token}

    # Getting latest transactions from TransferWise
    mock_get_latest_trans = mock.Mock(return_value=dummy_latest_transactions)

    # Filtering only new transactions
    cut_transactions = int(lastest_transactions_count / 2)
    new_transactions = dummy_latest_transactions[0:cut_transactions]

    # Preparing DDB query object
    ddb_query = mock.Mock()
    ddb_query.filter_new = mock.Mock(return_value=new_transactions)
    ddb_mock.query = mock.Mock(return_value=ddb_query)

    # Inserting transactions in DDB
    inserted_transactions = new_transactions
    ddb_query.insert = mock.Mock(return_value=inserted_transactions)

    mock_time_interval = mock.Mock()

    response = run_monitor(
        secret_key=secret_key,
        get_latest_transactions=mock_get_latest_trans,
        time_interval_func=mock_time_interval,
    )

    assert type(response) is dict
    trans_count = response.get('Transactions Count')
    assert type(trans_count) is dict
    assert trans_count.get('Retrieved from TransferWise') == \
        len(dummy_latest_transactions)
    assert trans_count.get('New (unseen) transactions') == \
        len(new_transactions)
    assert trans_count.get('Transactions stored for alerting') == \
        len(inserted_transactions)

    get_secret.assert_called_with(secret_key, load_json=True)

    mock_get_latest_trans.assert_called_with(
        api_token=api_token,
        time_interval=mock_time_interval(),
    )
