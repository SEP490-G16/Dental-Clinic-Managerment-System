import boto3
import random
from botocore.exceptions import ClientError
import os
import json

dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
table = dynamodb.Table(os.environ['DYNAMODB'])
client = boto3.client('ses', region_name='ap-southeast-1')


def gen_token(current_time_epoch):
    token = random.randint(100000, 999999)
    table.put_item(
        Item={
            'type': 'private-access',
            'epoch': 0,
            'otp': token,
            'exp': current_time_epoch + 330
        }
    )
    return token


def send_email(token, mail):
    SENDER = os.environ['SENDER_MAIL']
    RECIPIENT = mail

    SUBJECT = "Mã xác nhận cập nhật mật khẩu"

    BODY_TEXT = ("Hey Hi...\r\n"
                 "This email was sent with Amazon SES using the "
                 "AWS SDK for Python (Boto)."
                 )

    BODY_HTML = """<html>
    <head></head>
    <body>
    <p>Mã xác nhận của bạn là: </p>
    <h1>""" + str(token) + """</h1>
    <p>Mã xác nhận có thời hạn sử dụng trong vòng 1 phút.</p>
    <p>Quý khách vui lòng KHÔNG CUNG CẤP OTP cho bất cứ ai.</p>
    </body>
    </html>
                """

    response = client.send_email(
        Destination={
            'ToAddresses': [
                RECIPIENT,
            ],
        },
        Message={
            'Body': {
                'Html': {

                    'Data': BODY_HTML
                },
                'Text': {

                    'Data': BODY_TEXT
                },
            },
            'Subject': {

                'Data': SUBJECT
            },
        },
        Source=SENDER
    )
    return response


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
    id = event['pathParameters']['id']
    current_time_epoch = int(
        event['requestContext']['requestTimeEpoch']) / 1000
    mail = os.environ['MAIL_1'] if int(id) == int(1) else os.environ['MAIL_2']
    try:
        token = gen_token(int(current_time_epoch))
        res = send_email(token, mail)
        # return create_response(300, '', (token, mail))
        if res['ResponseMetadata']['HTTPStatusCode'] == 200:
            return create_response(200, 'OTP sent successful')
    except Exception as e:
        return create_response(500, 'Internal error', None, str(e.__class__.__name__))
    return create_response(500, 'OTP sent fail')
