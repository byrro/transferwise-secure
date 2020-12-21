import json
import os

from get_aws_secret import get_secret

from transaction import process_event


def handler(event, context):
    print(json.dumps(event))

    secret_arn = os.environ.get('SECRET_ARN')
    to_phone_number = os.environ.get('SEND_SMS_TO_PHONE_NUMBER')

    secret = get_secret(secret_arn, load_json=True)

    response = process_event(
        dynamodb_event=event,
        from_phone_number=secret['phone_number'],
        to_phone_number=to_phone_number,
    )

    print('RESPONSE from process_event():')
    print(json.dumps(response))

    return {
        "statusCode": 200,
        "body": json.dumps({
            "response": response,
        }),
    }
