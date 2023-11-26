import json
import pymysql
import os
import datetime
import decimal
import boto3
from boto3.dynamodb.conditions import Key, Attr

table = boto3.resource('dynamodb').Table(os.environ['DYNAMODB_TABLE'])

def transform_row(row):
    transformed_row = []
    for value in row:
        if isinstance(value, datetime.date):
            transformed_row.append(str(value))
        elif isinstance(value, decimal.Decimal):
            transformed_row.append(float(value))
        else:
            transformed_row.append(value)
    return tuple(transformed_row)


def get_mysql_error_message(error_code):
    error_messages = {
        1045: "Access denied for user",
        1049: "Unknown database",
        1146: "Table doesn't exist",
        1452: "Foreign key constraint fails", 
        1062: "Duplicate entry",
        1054: "Unknown column in field list"
    }
    return error_messages.get(error_code, "Unknown MySQL error")


def create_response(status_code, message, data=None, exception_type=None):
    response_body = {
        'message': message
    }

    if data is not None:
        response_body['data'] = data
    if exception_type is not None:
        response_body['type'] = exception_type

    return {
        'statusCode': status_code,
        'headers': {
            "Access-Control-Allow-Headers": "Access-Control-Allow-Headers, Access-Control-Allow-Methods, Accept, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers, Authorization",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "POST, PUT, PATCH, GET, DELETE, OPTIONS"
        },
        'body': json.dumps(response_body, ensure_ascii=False)
    }


def lambda_handler(event, context):
    conn = None
    cursor = None
    response = create_response(500, 'Internal error', None)
    if ('pathParameters' not in event or
            'start-date' not in event['pathParameters'] or
            not event['pathParameters']['start-date'] or
            'end-date' not in event['pathParameters'] or
            not event['pathParameters']['end-date'] or
            event['httpMethod'] != 'GET'):
        return create_response(400, 'Bad Request')
    try:
        res_data = {}
        conn = pymysql.connect(host=os.environ.get('HOST'), user=os.environ.get('USERNAME'), passwd=os.environ.get('PASSWORD'), db=os.environ.get('DATABASE'))
        cursor = conn.cursor()
        query = """
          SELECT 
            DATE(received_date) AS received_date, 
            SUM(quantity) AS total_medical_supply, 
            SUM(unit_price * quantity) AS total_price
          FROM medical_supply 
          WHERE `status` = 3 AND `received_date` BETWEEN FROM_UNIXTIME(%s) AND FROM_UNIXTIME(%s)
          GROUP BY DATE(received_date);
        """
        cursor.execute(query, (event['pathParameters']['start-date'], event['pathParameters']['end-date']))
        rows = cursor.fetchall()
        column_names = [column[0] for column in cursor.description]
        transformed_rows = [
            dict(zip(column_names, transform_row(row))) for row in rows]
        res_data['medical_supply'] = transformed_rows

        query = """
          SELECT 
            DATE(im.created_date) AS created_date, 
            COUNT(DISTINCT im.id) AS total_import_material, 
            SUM(mw.quantity_import * mw.price) AS total_price
          FROM import_material im LEFT JOIN material_warehouse mw ON im.id = mw.import_material_id
          WHERE im.status = 1 
            AND im.created_date BETWEEN FROM_UNIXTIME(%s) AND FROM_UNIXTIME(%s)
            AND mw.status != 0
          GROUP BY DATE(im.created_date);
        """
        cursor.execute(query, (event['pathParameters']['start-date'], event['pathParameters']['end-date']))
        rows = cursor.fetchall()
        column_names = [column[0] for column in cursor.description]
        transformed_rows = [
            dict(zip(column_names, transform_row(row))) for row in rows]
        res_data['import_material'] = transformed_rows

        dynamo_result = table.query(
            KeyConditionExpression=Key('type').eq('e') & Key('epoch').between(
                int(event['pathParameters']['start-date']),
                int(event['pathParameters']['end-date'])
            )
        )
        
        res_data['dynamo'] = str(dynamo_result.get('Items', []))
        
        response =  create_response(200, '', res_data)
    except pymysql.MySQLError as e:
        print("MySQL error:", e)
        error_message = get_mysql_error_message(e.args[0])
        status_code = 400 if e.args[0] in [1452, 1062, 1054] else 500
        response = create_response(status_code, error_message, None, str(e.__class__.__name__))
    except Exception as e:
        print("Error:", e)
        response = create_response(500, 'Internal error', None, str(e.__class__.__name__))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return response