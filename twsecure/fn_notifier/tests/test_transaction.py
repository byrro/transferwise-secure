import os
from unittest import mock

from transaction import (
    build_transaction_alert_message,
    get_transactions_from_event,
    get_table_name,
    process_event,
    SMS_MESSAGE_MAX_CHAR_LENGTH,
)


def twilio_response_generator(max):
    for i in range(0, max):
        yield {
            'message_id': f'sid-{i}',
            'outcome': 'confirmed',
        }


def transactions_generator(max):
    for i in range(0, max):
        yield {
            'transaction-hash': f'hash-{i}',
            'details': {
                'account': 'Dummy',
                'currency': 'XYZ',
                'value': f'{i}.00',
                'payee': f'Dummy Merchant {i}',
            },
        }


@mock.patch('transaction.get_transactions_from_event')
@mock.patch('transaction.send_message')
def test_process_event(
    send_message,
    get_transactions_mock,
    dynamodb_event,
    transactions_sample,
    from_phone_number,
    to_phone_number,
):
    get_transactions_mock.return_value = transactions_sample
    twilio_responses = twilio_response_generator(max=len(transactions_sample))
    send_message.side_effect = twilio_responses

    response = process_event(
        dynamodb_event=dynamodb_event,
        from_phone_number=from_phone_number,
        to_phone_number=to_phone_number,
    )

    assert type(response) is dict
    assert 'send_message_response' in response.keys()
    assert 'transactions' in response.keys()


@mock.patch('transaction.get_transactions_from_event')
@mock.patch('transaction.send_message')
def test_process_event_no_valid_transactions(
    send_message,
    get_transactions_mock,
    dynamodb_event,
    transactions_sample,
    from_phone_number,
    to_phone_number,
):
    get_transactions_mock.return_value = []

    response = process_event(
        dynamodb_event=dynamodb_event,
        from_phone_number=from_phone_number,
        to_phone_number=to_phone_number,
    )

    send_message.assert_not_called()

    assert type(response) is dict
    assert 'send_message_response' in response.keys()
    assert 'transactions' in response.keys()
    assert response['send_message_response'] is None
    assert type(response['transactions']) is list
    assert len(response['transactions']) == 0


def test_get_table_name(table_name):
    env_vars = {'TRANSACTIONS_TABLE_NAME': table_name}

    with mock.patch.dict(os.environ, env_vars):
        response = get_table_name()

        assert response == table_name


def test_get_transactions_from_event(
    table_name,
    dynamodb_event,
):
    env_vars = {'TRANSACTIONS_TABLE_NAME': table_name}

    with mock.patch.dict(os.environ, env_vars):
        expected_hashes = ['hash-1', 'hash-2', 'hash-3']

        items = get_transactions_from_event(event=dynamodb_event)

        assert type(items) is list
        assert len(items) == 3

        expected_details = ['account', 'currency', 'value', 'payee']

        for item in items:
            assert type(item) is dict
            assert 'transaction-hash' in item.keys()
            assert 'details' in item.keys()

            for key in expected_details:
                assert key in item['details'].keys()
                assert type(item['details'][key]) is str
                assert len(item['details'][key]) > 0

        item_hashes = [
            item['transaction-hash']
            for item in items
        ]

        for hash_ in expected_hashes:
            assert hash_ in item_hashes


def test_build_single_transaction_alert_message():
    transactions = [{
        'transaction-hash': 'hash-1',
        'details': {
            'account': 'Personal',
            'currency': 'XYZ',
            'value': '12.34',
            'payee': 'Merchant',
        },
    }]

    sms_msg = build_transaction_alert_message(transactions=transactions)

    assert sms_msg == 'Transferwise debit: XYZ 12.34 from Personal to Merchant (reply STOP to unsubscribe)'

    transactions = [{
        'transaction-hash': 'hash-2',
        'details': {
            'account': 'Business',
            'currency': 'XYZ',
            'value': '12.34',
            'payee': 'Undetermined',
        },
    }]

    sms_msg = build_transaction_alert_message(transactions=transactions)

    assert sms_msg == 'Transferwise debit: XYZ 12.34 from Business to Undetermined (reply STOP to unsubscribe)'  # NOQA


def test_build_multi_transactions_alert_message():
    # Just a couple messages
    transactions = list(transactions_generator(max=2))

    sms_msg = build_transaction_alert_message(transactions=transactions)

    assert sms_msg == 'Transferwise 2 debits to: Dummy Merchant 0 (0.00), Dummy Merchant 1 (1.00) (reply STOP to unsubscribe)'  # NOQA

    # Now too many transactions to test the string slice
    transactions = list(transactions_generator(max=200))

    sms_msg = build_transaction_alert_message(transactions=transactions)

    assert len(sms_msg) < SMS_MESSAGE_MAX_CHAR_LENGTH
    assert '... and others' in sms_msg


def test_send_sms():
    pass
