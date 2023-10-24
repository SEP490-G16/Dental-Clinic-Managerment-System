import json
import pymysql
import os
import datetime

conn = pymysql.connect(host=os.environ.get('HOST'),
                       user=os.environ.get('USERNAME'),
                       passwd=os.environ.get('PASSWORD'),
                       db=os.environ.get('DATABASE'))
cursor = conn.cursor()


def get_value_or_none(data, key):
    return data[key] if key in data else None


def lambda_handler(event, context):
    global conn, cursor

    if event['httpMethod'] != 'POST' or not event.get('body'):
        return {
            'statusCode': 400,
            'headers': {},
            'body': json.dumps({'message': 'Bad Request'})
        }

    try:
        data = json.loads(event['body'])

        required_fields = ['patient_name', 'phone_number',
                           'date_of_birth', 'gender', 'address']

        missing_fields = [
            field for field in required_fields if not data.get(field)]

        if missing_fields:
            return {
                'statusCode': 400,
                'headers': {},
                'body': json.dumps({'message': f"Fields {', '.join(missing_fields)} are required"})
            }

        query = """INSERT INTO `patient` (`patient_name`, `date_of_birth`, `gender`, `phone_number`, `full_medical_history`, 
                `dental_medical_history`, `email`, `address`, `description`, `profile_image`)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""

        cursor.execute(query, (data.get('patient_name'),
                               get_value_or_none(data, 'date_of_birth'),
                               get_value_or_none(data, 'gender'),
                               data.get('phone_number'),
                               get_value_or_none(data, 'full_medical_history'),
                               get_value_or_none(
                                   data, 'dental_medical_history'),
                               get_value_or_none(data, 'email'),
                               get_value_or_none(data, 'address'),
                               get_value_or_none(data, 'description'),
                               get_value_or_none(data, 'profile_image')))

        conn.commit()

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
