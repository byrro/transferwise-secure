from unittest import mock

from sms import (
    get_twilio_account_secret,
    get_twilio_client,
    send_message,
    SECRET_ARN,
)


@mock.patch('sms.get_secret')
def test_get_twilio_account_secret(get_secret):
    secret_key = 'dummy-key'
    secret_val = 'foobar'

    get_secret.return_value = {secret_key: secret_val}

    secret = get_twilio_account_secret(secret_key=secret_key)

    get_secret.assert_called_with(
        SECRET_ARN,
        load_json=True,
    )

    assert secret == secret_val


@mock.patch('sms.get_twilio_account_secret')
@mock.patch('sms.TwilioClient')
def test_get_twilio_client(client_mock, get_secret_mock):
    client_instance = mock.Mock()
    client_mock.return_value = client_instance

    secret_val = 'my-secret'
    get_secret_mock.return_value = secret_val

    # Try without providing secrets
    client = get_twilio_client()

    assert client == client_instance

    assert get_secret_mock.call_count == 2
    get_secret_mock.assert_has_calls([
        mock.call(secret_key='account_id'),
        mock.call(secret_key='api_token'),
    ])
    client_mock.assert_called_once_with(
        username=secret_val,
        password=secret_val,
    )

    # Try with custom secret args
    client_mock.reset_mock()
    get_secret_mock.reset_mock()

    account_id = 'account-id'
    api_token = 'api-token'

    client = get_twilio_client(account_id=account_id, api_token=api_token)

    assert client == client_instance
    get_secret_mock.assert_not_called()
    client_mock.assert_called_once_with(
        username=account_id,
        password=api_token,
    )


@mock.patch('sms.get_twilio_client')
def test_send_message(get_client_mock):
    # Mock Twilio response object
    twilio_response = mock.Mock()
    twilio_response.sid = '123'
    twilio_response.status = 'queued'
    twilio_response.error_code = None
    twilio_response.error_message = None

    # Mock Twilio message create method
    create_method = mock.Mock(return_value=twilio_response)

    # Mock Twilio client object
    client = mock.Mock()
    client.messages = mock.Mock()
    client.messages.create = create_method

    # Mock internal Twilio client factory function
    get_client_mock.return_value = client

    # Test without providing a custom client
    kwargs = {
        'message': 'Dummy message',
        'from_phone_number': '+1234567890',
        'to_phone_number': '+9876543210',
    }

    response = send_message(**kwargs)

    assert type(response) is dict
    assert response.get('message_id') == twilio_response.sid
    assert response.get('status') == twilio_response.status
    assert response.get('error_code') == twilio_response.error_code
    assert response.get('error_message') == twilio_response.error_message

    assert get_client_mock.called
    create_method.assert_called_once_with(
        body=kwargs['message'],
        from_=kwargs['from_phone_number'],
        to=kwargs['to_phone_number'],
    )

    # Test with a custom client object
    client.reset_mock()
    client.messages.reset_mock()
    client.messages.create.reset_mock()
    get_client_mock.reset_mock()

    kwargs['client'] = client

    response = send_message(**kwargs)

    assert not get_client_mock.called
    create_method.assert_called_once_with(
        body=kwargs['message'],
        from_=kwargs['from_phone_number'],
        to=kwargs['to_phone_number'],
    )
