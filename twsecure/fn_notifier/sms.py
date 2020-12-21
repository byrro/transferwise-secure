import os
from typing import Optional

from get_aws_secret import get_secret
from twilio.rest import Client as TwilioClient


SECRET_ARN = os.environ.get('SECRET_ARN')


def get_twilio_account_secret(
    secret_key: str,
    secret_arn: str = SECRET_ARN,
) -> tuple:
    secret = get_secret(secret_arn, load_json=True)

    return secret[secret_key]


def get_twilio_client(
    account_id: Optional[str] = None,
    api_token: Optional[str] = None,
) -> TwilioClient:
    if account_id is None:
        account_id = get_twilio_account_secret(secret_key='account_id')

    if api_token is None:
        api_token = get_twilio_account_secret(secret_key='api_token')

    return TwilioClient(
        username=account_id,
        password=api_token,
    )


def send_message(
    message: str,
    from_phone_number: str,
    to_phone_number: str,
    client: Optional[TwilioClient] = None,
) -> dict:
    if client is None:
        client = get_twilio_client()

    response = client.messages.create(
        body=message,
        from_=from_phone_number,
        to=to_phone_number,
    )

    return {
        'message_id': response.sid,
        'status': response.status,
        'error_code': response.error_code,
        'error_message': response.error_message,
    }
