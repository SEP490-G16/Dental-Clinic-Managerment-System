import json
import urllib3
import os
import boto3
import datetime
from urllib.parse import urlencode
# import sys
# sys.stdout = sys.stderr = open('/dev/stdout', 'w')
# import locale
# locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

http = urllib3.PoolManager()
test = http.request(
    'GET', 'https://api.telegram.org/bot6128285207:AAH5oNu1XkMOfPWtSEC9NrmbxQbdLm23Sko/sendMessage?chat_id=-957532052&text=trigger8h')

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
        print(res)
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


def send_zalo_message(access_token, phone, template_data):
    http = urllib3.PoolManager()

    url = 'https://business.openapi.zalo.me/message/template'

    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'secret_key': os.environ.get('SECRET_KEY'),
        'access_token': access_token
    }

    data = json.dumps({
        "access_token": access_token,
        "phone": phone,
        "template_id": 291078,
        "template_data": template_data
    }, ensure_ascii=False)
    print(data)
    response = http.request(
        'POST', url, body=data.encode('utf-8'), headers=headers)

    if response.status == 200:
        print(json.loads(response.data.decode('utf-8')))
        return json.loads(response.data.decode('utf-8'))
    else:
        print(json.loads(response.data.decode('utf-8')))
        return None


def test(access_token, phone, template_data):
    print(access_token)
    print(phone)
    print(template_data)


def lambda_handler(event, context):
    data = res_appointment.get("Item")
    access_token = get_access_token()
    # print(access_token)
    for key, value in data.items():
        if key not in ["type", "epoch"] and value.get('migrated') is False:
            dt = datetime.datetime.utcfromtimestamp(value.get('time') + 25200)
            dt1 = datetime.datetime.utcfromtimestamp(data.get('epoch') + 25200)
            phone_number = str(value.get('phone_number'))
            send_zalo_message(access_token=access_token,
                              phone=phone_number[1:] if phone_number.startswith(
                                  '+') else "84" + phone_number[1:],
                              template_data={
                                  "customer_name": value.get('patient_name'),
                                  "phone_doctor_binh": "0979066759",
                                  "phone_doctor_hoa": "0906235460",
                                  "content": str(value.get('procedure_name')),
                                  "time": "{:02d}:{:02d}".format(dt.hour, dt.minute),
                                  "appointment_date": "{:02d}/{:02d}/{:04d}".format(dt1.day, dt1.month, dt1.year),
                                  "patient_name": value.get('patient_name'),
                                  "patient_code": value.get('patient_id'),
                                  "customer": "/benhnhan-zalo/xac-nhan-lich-hen/{}/{}".format(data.get('epoch'), key),
                                  "change_appointment": "/benhnhan-zalo/doilichhen/{}/{}".format(data.get('epoch'), key)
                              })
    return data
