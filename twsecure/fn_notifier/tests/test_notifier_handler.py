import json
import os

from unittest import mock


@mock.patch('notifier.process_event')
@mock.patch('notifier.get_secret')
def test_handler(
    mock_get_secret,
    mock_process_event,
    dynamodb_event,
    from_phone_number,
    to_phone_number,
    secret_arn,
):
    env_vars = {
        'SEND_SMS_TO_PHONE_NUMBER': to_phone_number,
        'SECRET_ARN': secret_arn,
    }

    with mock.patch.dict(os.environ, env_vars):
        from notifier import handler

        process_response = {'foo': 'bar'}
        mock_process_event.return_value = process_response

        mock_get_secret.return_value = {
            'phone_number': from_phone_number,
        }

        expected_response = {
            'statusCode': 200,
            'body': json.dumps({'response': process_response}),
        }

        handler_response = handler(dynamodb_event, None)

        mock_process_event.assert_called_with(
            dynamodb_event=dynamodb_event,
            from_phone_number=mock_get_secret.return_value['phone_number'],
            to_phone_number=to_phone_number,
        )

        assert handler_response == expected_response
