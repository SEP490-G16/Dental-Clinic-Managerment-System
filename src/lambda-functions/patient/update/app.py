import json
import pymysql
import os
from datetime import datetime

conn = pymysql.connect(host=os.environ.get('HOST'),
                       user=os.environ.get('USERNAME'),
                       passwd=os.environ.get('PASSWORD'),
                       db=os.environ.get('DATABASE'))
cursor = conn.cursor()


def get_value_or_none(data, key):
    return data[key] if key in data else None


def lambda_handler(event, context):
    global conn, cursor

    if event['httpMethod'] != 'PUT' or not event.get('body') or not event.get('pathParameters') or 'id' not in event['pathParameters']:
        return {
            'statusCode': 400,
            'headers': {},
            'body': json.dumps({'message': 'Bad Request'})
        }

    try:
        data = json.loads(event['body'])
        patient_id = event['pathParameters']['id']

        # Kiểm tra trường name và phone_number
        if data.get('patient_name') is None or data.get('phone_number') is None:
            return {
                'statusCode': 400,
                'headers': {},
                'body': json.dumps({'message': 'patient_name and phone_number fields cannot be set to None'})
            }

        query = """
        UPDATE `patient` 
        SET patient_name=%s, date_of_birth=%s, gender=%s, phone_number=%s, full_medical_history=%s, 
            dental_medical_history=%s, email=%s, address=%s, description=%s, profile_image=%s, sub_phone_number=%s
        WHERE patient_id=%s;
        """
        date_of_birth = datetime.fromtimestamp(
            data.get('date_of_birth')).strftime('%Y-%m-%d')
        cursor.execute(query, (data.get('patient_name'),
                               date_of_birth,
                               get_value_or_none(data, 'gender'),
                               data.get('phone_number'),
                               get_value_or_none(data, 'full_medical_history'),
                               get_value_or_none(
                                   data, 'dental_medical_history'),
                               get_value_or_none(data, 'email'),
                               get_value_or_none(data, 'address'),
                               get_value_or_none(data, 'description'),
                               get_value_or_none(data, 'profile_image'),
                               get_value_or_none(data, 'sub_phone_number'),
                               patient_id))

        conn.commit()

        if cursor.rowcount == 0:  # Nếu không có bản ghi nào được cập nhật
            return {
                'statusCode': 404,
                'headers': {},
                'body': json.dumps({'message': 'Patient not found'})
            }

        return {
            'statusCode': 200,
            'headers': {},
            'body': json.dumps({'message': 'Patient updated successfully'})
        }
    except pymysql.MySQLError as e:
        print("MySQL error:", e)
        return {
            'statusCode': 500,
            'headers': {},
            'body': json.dumps({'message': 'Database error', 'type': str(e.__class__.__name__)})
        }
    except Exception as e:
        print("Error:", e)
        return {
            'statusCode': 500,
            'headers': {},
            'body': json.dumps({'message': 'Internal error', 'type': str(e.__class__.__name__)})
        }
