import json
import os
from typing import Callable, List

from sms import send_message

SMS_MESSAGE_MAX_CHAR_LENGTH = 300
SINGLE_TRANSACTION_MSG_TEMPLATE = 'Transferwise debit: {currency} ' \
    '{value} from {account} to {payee} (reply STOP to unsubscribe)'
MULTI_TRANSACTION_MSG_TEMPLATE = 'Transferwise {transactions_count} debits ' \
    'to: {payees} (reply STOP to unsubscribe)'


def process_event(
    dynamodb_event: dict,
    from_phone_number: str,
    to_phone_number: str,
) -> dict:
    transactions = get_transactions_from_event(event=dynamodb_event)
    response = None

    if len(transactions) > 0:
        message = build_transaction_alert_message(transactions)

        response = send_message(
            message=message,
            from_phone_number=from_phone_number,
            to_phone_number=to_phone_number,
        )

    return {
        'send_message_response': response,
        'transactions': transactions,
    }


def get_table_name():
    return os.environ['TRANSACTIONS_TABLE_NAME']


def get_transactions_from_event(
    event: dict,
    get_table_name: Callable = get_table_name,
) -> list:
    table_name = get_table_name()

    return [
        {
            'transaction-hash': record['dynamodb']['Keys']['transaction-hash']['S'],  # NOQA
            'details': json.loads(record['dynamodb']['NewImage']['details']['S']),  # NOQA
        }
        for record in event['Records']
        if table_name in record['eventSourceARN'] and
        record['eventName'] == 'INSERT'
    ]


def build_transaction_alert_message(
    transactions: List[dict],
    message_max_length: int = SMS_MESSAGE_MAX_CHAR_LENGTH,
    single_transaction_template: str = SINGLE_TRANSACTION_MSG_TEMPLATE,
    multi_transaction_template: str = MULTI_TRANSACTION_MSG_TEMPLATE,
) -> str:
    if len(transactions) == 1:
        return single_transaction_template.format(**transactions[0]['details'])

    max_payee_length = message_max_length - len(multi_transaction_template)

    payees = ', '.join([
        f'{t["details"]["payee"]} ({t["details"]["value"]})'
        for t in transactions
    ])

    if len(payees) > max_payee_length:
        payees = payees[0:max_payee_length] + '... and others'

    return multi_transaction_template.format(
        transactions_count=len(transactions),
        payees=payees,
    )
