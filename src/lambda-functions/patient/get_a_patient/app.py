import json
import pymysql
import os
import datetime

conn = pymysql.connect(host=os.environ.get('HOST'), user=os.environ.get(
    'USERNAME'), passwd=os.environ.get('PASSWORD'), db=os.environ.get('DATABASE'))
cursor = conn.cursor()


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

    column_names = [desc[0] for desc in cursor.description]

    result = []
    for row in cursor.fetchall():
        row_list = list(row)
        if isinstance(row_list[11], (datetime.date, datetime.datetime)):
            row_list[11] = row_list[11].isoformat()

        result.append(dict(zip(column_names, row_list)))

    cursor.close()
    conn.close()

    return {
        'statusCode': 200,
        'headers': {},
        'body': json.dumps(result)
    }
