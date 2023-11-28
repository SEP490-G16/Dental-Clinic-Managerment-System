import json
import urllib3
from urllib.parse import urlencode
import os

access_token = ''


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
        'refresh_token': os.environ.get('REFRESH_TOKEN')
    }

    encoded_data = urlencode(data)

    response = http.request('POST', url, body=encoded_data, headers=headers)

    if response.status == 200:
        res = json.loads(response.data.decode('utf-8'))
        return res['access_token']


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


def lambda_handler(event, context):
    global access_token
    access_token = get_access_token()
    send_zalo_message()
