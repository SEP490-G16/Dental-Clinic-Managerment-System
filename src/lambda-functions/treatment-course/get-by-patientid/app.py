import json
import pymysql
import os
import datetime

conn = pymysql.connect(host=os.environ.get('HOST'), user=os.environ.get(
    'USERNAME'), passwd=os.environ.get('PASSWORD'), db=os.environ.get('DATABASE'))
cursor = conn.cursor()


def transform_row(row):
    transformed_row = []
    for value in row:
        if isinstance(value, datetime.date):
            transformed_row.append(str(value))
        else:
            transformed_row.append(value)
    return tuple(transformed_row)


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
    if ('pathParameters' not in event or
            'id' not in event['pathParameters'] or
            not event['pathParameters']['id'] or
            event['httpMethod'] != 'GET'):
        return {
            'statusCode': 400,
            'headers': {},
            'body': json.dumps({'message': 'Bad Request'})
        }

    id = event['pathParameters']['id']

    try:
        query = """
        SELECT * FROM `treatment_course`
            WHERE `patient_id` = %s AND status != 0;
        """
        cursor.execute(query, (id))
        rows = cursor.fetchall()
        column_names = [column[0] for column in cursor.description]
        transformed_rows = [
            dict(zip(column_names, transform_row(row))) for row in rows]

        if len(transformed_rows) == 0:
            return {
                'statusCode': 404,
                'headers': {},
                'body': json.dumps({'message': 'Patient not found'}, ensure_ascii=False)
            }

        return {
            'statusCode': 200,
            'headers': {},
            'body': json.dumps(transformed_rows, ensure_ascii=False)
        }
    except pymysql.MySQLError as e:
        print("MySQL error:", e)
        error_message = get_mysql_error_message(e.args[0])
        return {
            'statusCode': 400 if e.args[0] in [1452, 1062, 1054] else 500,
            'headers': {},
            'body': json.dumps({'message': error_message, 'type': str(e.__class__.__name__)})
        }
    except Exception as e:
        print("Error:", e)
        return {
            'statusCode': 500,
            'headers': {},
            'body': json.dumps({'message': 'Internal error', 'type': str(e.__class__.__name__)})
        }
