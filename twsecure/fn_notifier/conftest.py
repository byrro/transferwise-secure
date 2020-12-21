import json

import pytest


@pytest.fixture
def from_phone_number():
    return '+9876543210'


@pytest.fixture
def to_phone_number():
    return '+1234567890'


@pytest.fixture
def secret_arn():
    return 'arn:secretsmanager:dummy'


@pytest.fixture
def table_name():
    return 'ddb-table-name'


@pytest.fixture
def dynamodb_event(table_name):
    return {
        "Records": [
            {
                "eventID": "c4ca4238a0b923820dcc509a6f75849b",
                "eventName": "INSERT",
                "eventVersion": "1.1",
                "eventSource": "aws:dynamodb",
                "awsRegion": "us-east-1",
                "dynamodb": {
                    "Keys": {
                        "transaction-hash": {
                            "S": "hash-1"
                        }
                    },
                    "NewImage": {
                        "transaction-hash": {
                            "S": "hash-1"
                        },
                        "details": {
                            "S": json.dumps({
                                'account': 'Dummy',
                                'currency': 'XYZ',
                                'value': '12.34',
                                'payee': 'Dummy Merchant'
                            }),
                        },
                    },
                    "ApproximateCreationDateTime": 1428537600,
                    "SequenceNumber": "4421584500000000017450439091",
                    "SizeBytes": 26,
                    "StreamViewType": "NEW_AND_OLD_IMAGES"
                },
                "eventSourceARN": f"arn:aws:dynamodb:us-east-1:123456789012:table/{table_name}/stream/2015-06-27T00:48:05.899"  # NOQA
            },
            {
                "eventID": "c4ca4238a0b923820dcc509a6f75849b",
                "eventName": "INSERT",
                "eventVersion": "1.1",
                "eventSource": "aws:dynamodb",
                "awsRegion": "us-east-1",
                "dynamodb": {
                    "Keys": {
                        "transaction-hash": {
                            "S": "hash-2"
                        }
                    },
                    "NewImage": {
                        "transaction-hash": {
                            "S": "hash-2"
                        },
                        "details": {
                            "S": json.dumps({
                                'account': 'Dummy',
                                'currency': 'XYZ',
                                'value': '50.00',
                                'payee': 'Dummy Recipient'
                            }),
                        },
                    },
                    "ApproximateCreationDateTime": 1428537600,
                    "SequenceNumber": "4421584500000000017450439091",
                    "SizeBytes": 26,
                    "StreamViewType": "NEW_AND_OLD_IMAGES"
                },
                "eventSourceARN": f"arn:aws:dynamodb:us-east-1:123456789012:table/{table_name}/stream/2015-06-27T00:48:05.899"  # NOQA
            },
            {
                "eventID": "c4ca4238a0b923820dcc509a6f75849b",
                "eventName": "INSERT",
                "eventVersion": "1.1",
                "eventSource": "aws:dynamodb",
                "awsRegion": "us-east-1",
                "dynamodb": {
                    "Keys": {
                        "transaction-hash": {
                            "S": "hash-3"
                        }
                    },
                    "NewImage": {
                        "transaction-hash": {
                            "S": "hash-3"
                        },
                        "details": {
                            "S": json.dumps({
                                'account': 'Dummy',
                                'currency': 'XYZ',
                                'value': '95.50',
                                'payee': 'Undetermined'
                            }),
                        },
                    },
                    "ApproximateCreationDateTime": 1428537600,
                    "SequenceNumber": "4421584500000000017450439091",
                    "SizeBytes": 26,
                    "StreamViewType": "NEW_AND_OLD_IMAGES"
                },
                "eventSourceARN": f"arn:aws:dynamodb:us-east-1:123456789012:table/{table_name}/stream/2015-06-27T00:48:05.899"  # NOQA
            },
            {
                "eventID": "c4ca4238a0b923820dcc509a6f75849b",
                "eventName": "INSERT",
                "eventVersion": "1.1",
                "eventSource": "aws:dynamodb",
                "awsRegion": "us-east-1",
                "dynamodb": {
                    "Keys": {
                        "transaction-hash": {
                            "S": "hash-4"
                        }
                    },
                    "NewImage": {
                        "transaction-hash": {
                            "S": "hash-4"
                        },
                        "details": {
                            "S": json.dumps({
                                'account': 'Dummy',
                                'currency': 'XYZ',
                                'value': '95.50',
                                'payee': 'Undetermined'
                            }),
                        },
                    },
                    "ApproximateCreationDateTime": 1428537600,
                    "SequenceNumber": "4421584500000000017450439091",
                    "SizeBytes": 26,
                    "StreamViewType": "NEW_AND_OLD_IMAGES"
                },
                "eventSourceARN": f"arn:aws:dynamodb:us-east-1:123456789012:table/invalid-table/stream/2015-06-27T00:48:05.899"  # NOQA
            },
            {
                "eventID": "c81e728d9d4c2f636f067f89cc14862c",
                "eventName": "MODIFY",
                "eventVersion": "1.1",
                "eventSource": "aws:dynamodb",
                "awsRegion": "us-east-1",
                "dynamodb": {
                    "Keys": {
                        "Id": {
                            "N": "101"
                        }
                    },
                    "NewImage": {
                        "Message": {
                            "S": "This item has changed"
                        },
                        "Id": {
                            "N": "101"
                        }
                    },
                    "OldImage": {
                        "Message": {
                            "S": "New item!"
                        },
                        "Id": {
                            "N": "101"
                        }
                    },
                    "ApproximateCreationDateTime": 1428537600,
                    "SequenceNumber": "4421584500000000017450439092",
                    "SizeBytes": 59,
                    "StreamViewType": "NEW_AND_OLD_IMAGES"
                },
                "eventSourceARN": "arn:aws:dynamodb:us-east-1:123456789012:table/ExampleTableWithStream/stream/2015-06-27T00:48:05.899"  # NOQA
            },
            {
                "eventID": "eccbc87e4b5ce2fe28308fd9f2a7baf3",
                "eventName": "REMOVE",
                "eventVersion": "1.1",
                "eventSource": "aws:dynamodb",
                "awsRegion": "us-east-1",
                "dynamodb": {
                    "Keys": {
                        "Id": {
                            "N": "101"
                        }
                    },
                    "OldImage": {
                        "Message": {
                            "S": "This item has changed"
                        },
                        "Id": {
                            "N": "101"
                        }
                    },
                    "ApproximateCreationDateTime": 1428537600,
                    "SequenceNumber": "4421584500000000017450439093",
                    "SizeBytes": 38,
                    "StreamViewType": "NEW_AND_OLD_IMAGES"
                },
                "eventSourceARN": "arn:aws:dynamodb:us-east-1:123456789012:table/ExampleTableWithStream/stream/2015-06-27T00:48:05.899"  # NOQA
            }
        ]
    }


@pytest.fixture
def transactions_sample():
    return [
        {
            'transaction-hash': 'hash-1',
            'details': {
                'account': 'Dummy',
                'currency': 'XYZ',
                'value': '12.34',
                'payee': 'Dummy Merchant',
            },
        },
        {
            'transaction-hash': 'hash-2',
            'details': {
                'account': 'Dummy',
                'currency': 'XYZ',
                'value': '50.00',
                'payee': 'Dummy Recipient',
            },
        },
        {
            'transaction-hash': 'hash-3',
            'details': {
                'account': 'Dummy',
                'currency': 'XYZ',
                'value': '95.50',
                'payee': 'Undetermined',
            },
        },
    ]
