#!/usr/bin/python3 Python3
from functools import partial
import json
import os

from datetime_routines import last_delta_interval
import transferwise


def handler(event, context):
    print(json.dumps(event))

    delta_unit = os.environ.get('TIME_DELTA_UNIT')
    delta_value = os.environ.get('TIME_DELTA_VALUE')

    monitor_kwargs = {}

    if delta_unit is not None and delta_value is not None:
        monitor_kwargs['time_interval_func'] = partial(
            last_delta_interval,
            delta_period={delta_unit: int(delta_value)},
        )

    tw_monitor = transferwise.monitor()
    response = tw_monitor.run(**monitor_kwargs)

    print('RESPONSE from tw_monitor.run():')
    print(json.dumps(response))

    return {
        'statusCode': 200,
        'body': json.dumps({
            'response': response,
        }),
    }
