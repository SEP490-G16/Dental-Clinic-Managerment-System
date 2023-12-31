import json
import pymysql
import os
import datetime


def transform_row(row):
    transformed_row = []
    for value in row:
        if isinstance(value, datetime.date):
            transformed_row.append(str(value))
        else:
            transformed_row.append(value)
    return tuple(transformed_row)


def lambda_handler(event, context):
    # global conn, cursor
    conn = pymysql.connect(host=os.environ.get('HOST'), user=os.environ.get(
        'USERNAME'), passwd=os.environ.get('PASSWORD'), db=os.environ.get('DATABASE'))
    cursor = conn.cursor()
    if ('pathParameters' not in event or
            'id' not in event['pathParameters'] or
            not event['pathParameters']['id'] or
            event['httpMethod'] != 'GET'):
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

    patient_id = event['pathParameters']['id']
    query = "SELECT * FROM `patient` WHERE patient_id = %s AND `active` != 0;"
    cursor.execute(query, (patient_id))
    # try:
    #     cursor.execute(query, (patient_id))
    # except pymysql.OperationalError:
    #     conn.ping(reconnect=True)
    #     cursor.execute(query, (patient_id))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    transformed_rows = [
        dict(zip(column_names, transform_row(row))) for row in rows]

    # cursor.close()
    # conn.close()

    # Kiểm tra nếu không tìm thấy bản ghi nào
    if len(transformed_rows) == 0:
        return {
            'statusCode': 404,
            'headers': {
                "Access-Control-Allow-Headers": "Access-Control-Allow-Headers, Access-Control-Allow-Methods, Accept, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers, Authorization",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "POST, PUT, PATCH, GET, DELETE, OPTIONS"
            },
            'body': json.dumps({'message': 'Patient not found'}, ensure_ascii=False)
        }

    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Headers": "Access-Control-Allow-Headers, Access-Control-Allow-Methods, Accept, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers, Authorization",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "POST, PUT, PATCH, GET, DELETE, OPTIONS"
        },
        'body': json.dumps(transformed_rows[0], ensure_ascii=False)
    }
