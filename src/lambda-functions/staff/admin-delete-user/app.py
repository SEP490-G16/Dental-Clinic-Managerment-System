import boto3
import json
import os
from datetime import datetime

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
    # Tạo client Cognito
    client = boto3.client('cognito-idp')

    # Giả sử bạn nhận username qua event, ví dụ từ API Gateway
    username = event['pathParameters']['username']
    user_pool_id = os.environ.get('USERPOOLID')

    # Xóa người dùng
    try:
        response = client.admin_delete_user(
            UserPoolId=user_pool_id,
            Username=username
        )
        return create_response(200, message='User deleted successfully.')
    except Exception as e:
        return create_response(500, message=str(e))