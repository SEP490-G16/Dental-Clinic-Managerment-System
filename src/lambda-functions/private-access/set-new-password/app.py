import json
import os
import boto3
import datetime

dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
table = dynamodb.Table(os.environ['DYNAMODB'])
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
    try:
        data = json.loads(event['body'])
        required_fields = ['otp', 'new_password']

        missing_fields = [
            field for field in required_fields if not data.get(field)]

        if missing_fields:
            return create_response(400, f"Fields {', '.join(missing_fields)} are required")

        private_access = table.get_item(
            Key={
                'type': 'private-access',
                'epoch': int(0)
            }
        )

        if private_access['Item']['otp'] != data['otp']:
            return create_response(400, "Token invalid!")
        current_time_epoch = int(datetime.datetime.now().timestamp())

        if private_access['Item']['exp'] <= current_time_epoch:
            return create_response(400, "Token has expired!")

        res = json.loads(cognito.admin_set_user_password(
            UserPoolId=os.environ['USER_POOL_ID'],
            Username='letan',
            Password=data['new_password'],
            Permanent=True
        ))

        if res['ResponseMetadata']['HTTPStatusCode'] == 200:
            return create_response(200, 'Change password successful')
    except Exception as e:
        return create_response(500, 'Internal error', None, str(e.__class__.__name__))
    return create_response(500, message='Internal error')
