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
    global conn, cursor
    if ('pathParameters' not in event or
            'name_prefix' not in event['pathParameters'] or
            'paging' not in event['pathParameters'] or
            not event['pathParameters']['name_prefix'] or
            event['httpMethod'] != 'GET'):
        return {
            'statusCode': 400,
            'headers': {},
            'body': json.dumps({'message': 'Bad Request'})
        }

    name_prefix = event['pathParameters']['name_prefix']
    try:
        page_number = int(event['pathParameters']['paging'])
        offset = (page_number - 1) * 10
    except ValueError:
        return {
            'statusCode': 400,
            'headers': {},
            'body': json.dumps({'message': 'Invalid paging value'})
        }

    query = """
        SELECT * FROM `patient`
        WHERE patient_name LIKE %s AND active = 1
        ORDER BY created_date DESC
        LIMIT 11 OFFSET %s;
    """
    cursor.execute(query, ("%" + name_prefix + "%", offset))
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
