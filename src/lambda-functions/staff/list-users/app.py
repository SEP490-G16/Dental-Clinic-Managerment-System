import json
import boto3
import os
from datetime import datetime
from botocore.exceptions import ClientError

cognito_client = boto3.client('cognito-idp')


def serialize_date(o):
    if isinstance(o, datetime):
        return o.isoformat()


def create_response(status_code, message, data=None, exception_type=None):
    response_body = {
        'message': message
    }

    if data is not None:
        response_body['data'] = data
    if exception_type is not None:
        response_body['type'] = exception_type

    return {
        'statusCode': status_code,
        'headers': {
            "Access-Control-Allow-Headers": "Access-Control-Allow-Headers, Access-Control-Allow-Methods, Accept, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers, Authorization",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "POST, PUT, PATCH, GET, DELETE, OPTIONS"
        },
        'body': json.dumps(response_body, default=serialize_date, ensure_ascii=False)
    }


def lambda_handler(event, context):

    user_pool_id = os.environ.get('USERPOOLID')

    try:
        response = cognito_client.list_users(UserPoolId=user_pool_id)
        users = [user for user in response['Users']
                 if user["Username"] != "private-access"]

        return create_response(200, users)
    except ClientError as e:
        print(e)
        return create_response(500, 'Internal error')
