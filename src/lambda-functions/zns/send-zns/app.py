import json
import urllib3
import os
import boto3
import datetime
from urllib.parse import urlencode

dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-1')
table = dynamodb.Table(os.environ['DYNAMODB'])

epoch_time = (datetime.datetime.now() + datetime.timedelta(days=1)
              ).replace(hour=0, minute=0, second=0, microsecond=0).timestamp() - 25200

res_appointment = table.get_item(
    Key={
        'type': 'a',
        'epoch': int(epoch_time)
    }
)

table_res = table.get_item(
    Key={
        'type': 'zns',
        'epoch': 0
    }
)

refresh_token = table_res.get('Item', {}).get('refresh_token', None)


def get_access_token():
    http = urllib3.PoolManager()

    url = 'https://oauth.zaloapp.com/v4/oa/access_token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'secret_key': os.environ.get('SECRET_KEY')
    }

    data = {
        'app_id': os.environ.get('APP_ID'),
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }

    encoded_data = urlencode(data)

    response = http.request('POST', url, body=encoded_data, headers=headers)

    if response.status == 200:
        res = json.loads(response.data.decode('utf-8'))
        table.put_item(
            Item={
                'type': 'zns',
                'epoch': 0,
                'refresh_token': res['refresh_token']
            }
        )
        return res['access_token']
    else:
        print(json.loads(response.data.decode('utf-8')))
        return None


def send_zalo_message():
    http = urllib3.PoolManager()

    url = 'https://business.openapi.zalo.me/message/template'

    headers = {
        'Content-Type': 'application/json',
        'secret_key': os.environ.get('SECRET_KEY'),
        'access_token': access_token
    }

    data = json.dumps({
        "access_token": access_token,
        "phone": "84966214037",
        "template_id": 291078,
        "template_data": {
            "customer_name": "Nguyễn Kiều Tuấn Anh c",
            "phone_doctor_binh": "0966214037",
            "phone_doctor_hoa": "0987654321",
            "content": "đến giờ cơm rồi đại vương ơi",
            "time": "12h trưa",
            "appointment_date": "23/11/2023",
            "patient_name": "Nguyễn Kiều Tuấn Anh p",
            "patient_code": "P-000001",
            "customer": "/xac-nhan-lich-hen",
            "change_appointment": "/benhnhan-zalo/doilichhen/1699894800000/4969d180-c922-479d-918f-ee6642c1e6a1"
        }
    }).encode('utf-8')

    response = http.request('POST', url, body=data, headers=headers)

    if response.status == 200:
        return json.loads(response.data.decode('utf-8'))
    else:
        return None


def test(access_token, phone, template_data):
    print(phone)
    print(template_data)


def lambda_handler(event, context):
    data = res_appointment.get("Item")
    # access_token = get_access_token()
    for key, value in data.items():
        if key not in ["type", "epoch"]:
            dt = datetime.datetime.utcfromtimestamp(value.get('time') + 25200)
            test(access_token="access_token",
                 phone="phone",
                 template_data={
                     "customer_name": value.get('patient_name'),
                     "phone_doctor_binh": "123",
                     "phone_doctor_hoa": "123",
                     "content": "",
                     "time": "{:02d}:{:02d}".format(dt.hour, dt.minute),
                     "appointment_date": "{:02d}/{:02d}/{:04d}".format(dt.day, dt.month, dt.year),
                     "patient_name": value.get('patient_name'),
                     "patient_code": value.get('patient_id'),
                     "customer": "/xac-nhan-lich-hen",
                     "change_appointment": "/benhnhan-zalo/doilichhen/{}/{}".format(data.get('epoch'), key)
                 })
    return data
