#!/.env/bin/python Python3
import json
import logging

import boto3
import botocore
import load_config

from dynamodb_local_items import generate_put_items


log = logging.getLogger()
logging.basicConfig(level=logging.INFO)


def setup(port, tables,  put_items):
    log.info('## Starting setup of local DynamoDB...')

    dynamodb = boto3.client(
        service_name='dynamodb',
        endpoint_url=f'http://localhost:{port}',
        verify=False,
        region_name='us-east-1',
        aws_access_key_id='LOCAL_ACCESS_KEY_ID',
        aws_secret_access_key='LOCAL_SECRET_ACCESS_KEY',
        config=botocore.client.Config(connect_timeout=5, read_timeout=5)
    )

    for table in tables:
        try:
            dynamodb.create_table(**convert_table_schema(table))
        except Exception as exc:
            log.exception(exc)
            log.error(f'\n-> Could not create table "{table["name"]}"\n')
        else:
            log.info(f'## Created table "{table.get("name")}"')

    for table_name, items in put_items.items():
        for item in items:
            try:
                dynamodb.put_item(TableName=table_name, Item=item)
            except Exception as exc:
                log.exception(exc)
                log.error(f'\n-> Could not put item in table: {table_name}, {item}\n')  # NOQA
            else:
                log.info(f'## Inserted item in {table_name}: {json.dumps(item)}')  # NOQA

    log.info('## All set with DynamoDB Local!')


def convert_table_schema(table: dict):
    schema = table['schema'].items()

    return {
        'TableName': table['name'],
        'BillingMode': 'PAY_PER_REQUEST',
        'AttributeDefinitions': [
            {
                'AttributeName': attr,
                'AttributeType': typ.split(',')[0],
            }
            for attr, typ in schema
        ],
        'KeySchema': [
            {
                'AttributeName': attr,
                'KeyType': typ.split(',')[1],
            }
            for attr, typ in schema
            if 'HASH' in typ or 'RANGE' in typ
        ]
    }


def aws_yaml_constructor(loader, node):
    return loader.construct_scalar(node)


if __name__ == '__main__':
    template = load_config.sam_template()
    transactions_table_name = template['Resources']['TransactionTable']['Properties']['TableName']  # NOQA

    # # Get local DynamoDB Setup
    # with open('dynamodb-local.yaml', 'r') as file:
    ddb_local = load_config.dynamodb_local()
    ddb_local_port = ddb_local['port']

    # Specify which tables should be created in local DynamoDB
    tables = [
        {
            'name': transactions_table_name,
            'schema': {
                'transaction-hash': 'S,HASH',
            },
        },
    ]

    # Specify items that should be inserted in DynamoDB local tables
    put_items = generate_put_items(
        table_names={'transactions': transactions_table_name},
    )

    # Run the DynamoDB setup routine
    setup(port=ddb_local_port, tables=tables, put_items=put_items)
