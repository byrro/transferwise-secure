import json


def generate_put_items(table_names):
    return {
        table_names['transactions']: generate_transaction_items(),
    }


def generate_transaction_items():
    return [
        {
            'transaction-hash': {'S': 'abc123abc123abc123abc123abc123ab'},
            'details': {'S': json.dumps({
                'account': 'Dummy',
                'currency': 'USD',
                'value': '12.34',
                'payee': 'Dummy Merchant',
            })},
            'ttl': {'N': str(1234567890)},
        },
    ]
