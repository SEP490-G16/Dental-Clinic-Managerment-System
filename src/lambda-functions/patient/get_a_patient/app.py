import json
import pymysql
import os

conn = pymysql.connect(host=os.environ.get('HOST'), user=os.environ.get(
    'USERNAME'), passwd=os.environ.get('PASSWORD'), db=os.environ.get('DATABASE'))
cursor = conn.cursor()


def lambda_handler(message, context):
    if ('pathParameters' not in message or
            message['httpMethod'] != 'GET'):
        return {
            'statusCode': 400,
            'headers': {},
            'body': json.dumps({'msg': 'Bad Request'})
        }

    patient_id = message['pathParameters']['id']
    query = "SELECT * FROM `patient` WHERE patient_id = %s;"
    cursor.execute(query, (patient_id))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return {
        'statusCode': 200,
        'headers': {},
        'body': json.dumps(rows)
    }
