import boto3
import random
from botocore.exceptions import ClientError
import os
import json

cognito = boto3.client('cognito-idp', region_name='ap-southeast-1')


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
        'body': json.dumps(response_body, ensure_ascii=False)
    }


def lambda_handler(event, context):
    data = json.loads(event['body'])
    try:
        exp = int(int(event['requestContext']
                  ['requestTimeEpoch']) / 1000) + 3600
        response = cognito.admin_update_user_attributes(
            UserPoolId=os.environ['USER_POOL_ID'],
            Username='private-access',
            UserAttributes=[
                {
                    'Name': 'custom:DOB',
                    'Value': str(exp)
                }
            ]
        )
        response = cognito.admin_initiate_auth(
            UserPoolId=os.environ['USER_POOL_ID'],
            ClientId=os.environ['CLIENT_ID'],
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={
                'USERNAME': 'private-access',
                'PASSWORD': data['access_code']
            }
        )
        if int(response['ResponseMetadata']['HTTPStatusCode']) == 200:
            return create_response(200, '', response['AuthenticationResult']['AccessToken'])
    except Exception as e:
        return create_response(500, 'Internal error', None, str(e.__class__.__name__))
    return create_response(500, 'Invalid Access Code')
