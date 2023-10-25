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

    query = "SELECT * FROM `medical_procedure_group` WHERE `active` != 0;"
    rows = cursor.execute(query)
    column_names = [column[0] for column in cursor.description]
    transformed_rows = [
        dict(zip(column_names, transform_row(row))) for row in rows]

    if len(transformed_rows) == 0:
        return {
            'statusCode': 404,
            'headers': {},
            'body': json.dumps({'message': 'medical procedure group not found'}, ensure_ascii=False)
        }

    return {
        'statusCode': 200,
        'headers': {},
        'body': json.dumps(transformed_rows[0], ensure_ascii=False)
    }
