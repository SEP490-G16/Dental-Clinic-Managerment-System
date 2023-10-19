import json
import pymysql
import os
import datetime

conn = pymysql.connect(host=os.environ.get('HOST'),
                       user=os.environ.get('USERNAME'),
                       passwd=os.environ.get('PASSWORD'),
                       db=os.environ.get('DATABASE'))
cursor = conn.cursor()


def lambda_handler(event, context):
    global conn, cursor

    # Kiểm tra request method và nội dung body
    if event['httpMethod'] != 'POST' or not event.get('body'):
        return {
            'statusCode': 400,
            'headers': {},
            'body': json.dumps({'message': 'Bad Request'})
        }

    try:
        data = json.loads(event['body'])

        # Insert dữ liệu vào bảng patient
        query = """INSERT INTO `patient` (`patient_name`, `date_of_birth`, `gender`, `phone_number`, `full_medical_history`, 
                 `dental_medical_history`, `email`, `address`, `description`, `profile_image`)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""

        cursor.execute(query, (data.get('patient_name'),
                               data.get('date_of_birth'),
                               data.get('gender'),
                               data.get('phone_number'),
                               data.get('full_medical_history'),
                               data.get('dental_medical_history'),
                               data.get('email'),
                               data.get('address'),
                               data.get('description'),
                               data.get('profile_image')))

        conn.commit()

        # Đáp trả thành công
        return {
            'statusCode': 201,
            'headers': {},
            'body': json.dumps({'message': 'Patient created successfully'})
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
