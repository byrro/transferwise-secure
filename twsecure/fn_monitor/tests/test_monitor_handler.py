import os
import json
from unittest import mock

import monitor


@mock.patch('transferwise.monitor')
def test_handler(transferwise_monitor):
    monitor_response = {'foo': 'bar'}
    tw_monitor = mock.Mock()
    tw_monitor.run = mock.Mock(return_value=monitor_response)
    transferwise_monitor.return_value = tw_monitor

    response = monitor.handler({}, None)

    transferwise_monitor.assert_called_with()
    tw_monitor.run.assert_called_with()
    assert type(response) is dict
    assert response.get('statusCode') == 200
    assert response.get('body') == json.dumps({'response': monitor_response})


@mock.patch('transferwise.monitor')
@mock.patch('monitor.last_delta_interval')
@mock.patch('monitor.partial')
def test_handler_custom_delta_env_vars(
    mock_partial,
    mock_last_delta_interval,
    mock_transferwise_monitor,
):
    time_unit = 'days'
    time_value = 7

    env_vars = {
        'TIME_DELTA_UNIT': time_unit,
        'TIME_DELTA_VALUE': str(time_value),
    }

    with mock.patch.dict(os.environ, env_vars):
        monitor_response = {'foo': 'bar'}
        tw_monitor = mock.Mock()
        tw_monitor.run = mock.Mock(return_value=monitor_response)
        mock_transferwise_monitor.return_value = tw_monitor

        time_interval = {
            'start': '2020-06-10T00:00:00Z',
            'end': '2020-06-17T00:00:00Z',
        }
        mock_last_delta_interval.return_value = time_interval

        mock_partial.return_value = mock_last_delta_interval

        response = monitor.handler({}, None)

        mock_partial.assert_called_with(
            mock_last_delta_interval,
            delta_period={time_unit: time_value}
        )
        mock_transferwise_monitor.assert_called_with()
        tw_monitor.run.assert_called_with(
            time_interval_func=mock_partial.return_value,
        )
        assert type(response) is dict
        assert response.get('statusCode') == 200
        assert response.get('body') == json.dumps({'response': monitor_response})  # NOQA
