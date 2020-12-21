#! /usr/bin/python3.8 Python3.8
import load_config


local_env = load_config.lambda_environ('MonitorFunction', '../local.json')

# with open('../../.env/local.json', 'r') as file:
#     local_env = json.loads(file.read())['MonitorFunction']

# with open('../template.yaml', 'r') as file:
#     template = ...

sam = load_config.sam_template('../template.yaml')


LOCAL_ENV_VARS = {
    'LOCAL_ENV_VARS_LOADED': 'true',
    'AWS_SAM_LOCAL': 'true',
    # 'AWS_EXECUTION_ENV': ...,
    # 'AWS_LAMBDA_FUNCTION_NAME': ...,
    'AWS_REGION': 'us-east-1',
    'AWS_ACCESS_KEY_ID': 'LOCAL_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY': 'LOCAL_SECRET_ACCESS_KEY',
    'LOGGER_NAME': 'MONITOR_LOGGER',
    'SECRET_ARN': local_env['SECRET_ARN'],
    'TRANSACTIONS_TABLE_NAME': local_env['TRANSACTIONS_TABLE_NAME'],
    'MAX_NEW_TRANSACTIONS_PER_EXECUTION': '50',
    'DYNAMODB_TTL_IN_DAYS': '7'
}
