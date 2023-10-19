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


def lambda_handler(event, context):
    if ('pathParameters' not in event or
            event['httpMethod'] != 'GET'):
        return {
            'statusCode': 400,
            'headers': {},
            'body': json.dumps({'msg': 'Bad Request'})
        }

    patient_id = event['pathParameters']['id']
    query = "SELECT * FROM `patient` WHERE patient_id = %s;"
    cursor.execute(query, (patient_id))
    rows = cursor.fetchall()

    transformed_rows = [transform_row(row) for row in rows]

    cursor.close()
    conn.close()

    # Kiểm tra nếu không tìm thấy bản ghi nào
    if len(transformed_rows) == 0:
        return {
            'statusCode': 404,
            'headers': {},
            'body': json.dumps({'msg': 'Patient not found'}, ensure_ascii=False)
        }

    return {
        'statusCode': 200,
        'headers': {},
        'body': json.dumps(transformed_rows, ensure_ascii=False)
    }
