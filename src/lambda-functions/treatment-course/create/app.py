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


def get_mysql_error_message(error_code):
    error_messages = {
        1045: "Access denied for user",
        1049: "Unknown database",
        1146: "Table doesn't exist",
        1452: "Foreign key constraint fails",  # Lỗi khóa ngoại
        1062: "Duplicate entry",  # Lỗi trùng lắp dữ liệu
        1054: "Unknown column in field list"  # Lỗi cột không tồn tại
    }
    return error_messages.get(error_code, "Unknown MySQL error")


def lambda_handler(event, context):
    global conn, cursor

    if event['httpMethod'] != 'POST' or not event.get('body'):
        return {
            'statusCode': 400,
            'headers': {
                "Access-Control-Allow-Headers": "Access-Control-Allow-Headers, Access-Control-Allow-Methods, Accept, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers, Authorization",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "POST, PUT, PATCH, GET, DELETE, OPTIONS"
            },
            'body': json.dumps({'message': 'Bad Request'})
        }

    try:
        data = json.loads(event['body'])

        required_fields = ['patient_id', 'name']

        missing_fields = [
            field for field in required_fields if not data.get(field)]

        if missing_fields:
            return {
                'statusCode': 400,
                'headers': {
                    "Access-Control-Allow-Headers": "Access-Control-Allow-Headers, Access-Control-Allow-Methods, Accept, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers, Authorization",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Allow-Methods": "POST, PUT, PATCH, GET, DELETE, OPTIONS"
                },
                'body': json.dumps({'message': f"Fields {', '.join(missing_fields)} are required"})
            }

        query = """
        INSERT INTO `treatment_course` 
        (`patient_id`, `description`, `name`, `chief_complaint`, `provisional_diagnosis`, `differential_diagnosis`) 
        VALUES 
        (%s, %s, %s, %s, %s, %s);
        """

        cursor.execute(query, (data.get('patient_id'),
                               get_value_or_none(data, 'description'),
                               data.get('name'),
                               get_value_or_none(data, 'chief_complaint'),
                               get_value_or_none(data, 'provisional_diagnosis'),
                               get_value_or_none(data, 'differential_diagnosis')))

        cursor.execute("SELECT treatment_course_id FROM treatment_course ORDER BY treatment_course_id DESC LIMIT 1;")
        row = cursor.fetchone()
        id = row[0]
        conn.commit()

        return {
            'statusCode': 201,
            'headers': {
                "Access-Control-Allow-Headers": "Access-Control-Allow-Headers, Access-Control-Allow-Methods, Accept, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers, Authorization",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "POST, PUT, PATCH, GET, DELETE, OPTIONS"
            },
            'body': json.dumps({'message': 'Treatment course created successfully', 'treatment_course_id': id})
        }
    except pymysql.MySQLError as e:
        print("MySQL error:", e)
        error_message = get_mysql_error_message(e.args[0])
        return {
            'statusCode': 400 if e.args[0] in [1452, 1062, 1054] else 500,
            'headers': {
                "Access-Control-Allow-Headers": "Access-Control-Allow-Headers, Access-Control-Allow-Methods, Accept, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers, Authorization",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "POST, PUT, PATCH, GET, DELETE, OPTIONS"
            },
            'body': json.dumps({'message': error_message, 'type': str(e.__class__.__name__)})
        }
    except Exception as e:
        print("Error:", e)
        return {
            'statusCode': 500,
            'headers': {
                "Access-Control-Allow-Headers": "Access-Control-Allow-Headers, Access-Control-Allow-Methods, Accept, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers, Authorization",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "POST, PUT, PATCH, GET, DELETE, OPTIONS"
            },
            'body': json.dumps({'message': 'Internal error', 'type': str(e.__class__.__name__)})
        }
