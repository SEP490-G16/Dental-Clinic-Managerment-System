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
            'paging' not in event['pathParameters'] or
            not event['pathParameters']['paging'] or
            event['httpMethod'] != 'GET'):
        return create_response(400, 'Bad Request')
    
    if int(event['pathParameters']['end-date']) - int(event['pathParameters']['start-date']) > 2678600:
        return create_response(400, 'Bad Request')
    try:
        page_number = int(event['pathParameters']['paging'])
        offset = (page_number - 1) * 10
    except ValueError:
        return create_response(400, 'Invalid paging value')
    try:
        conn = pymysql.connect(host=os.environ.get('HOST'), user=os.environ.get('USERNAME'), passwd=os.environ.get('PASSWORD'), db=os.environ.get('DATABASE'))
        cursor = conn.cursor()
        query = """
            SELECT 
                im.id, 
                im.created_date, 
                im.creator, 
                im.description, 
                im.status, 
                SUM(mw.quantity_import * mw.price  * (1 - CAST(mw.discount AS DECIMAL(10,2)))) AS total
            FROM 
                import_material im
            LEFT JOIN 
                material_warehouse mw ON im.id = mw.import_material_id
            WHERE 
                mw.status = 1 AND im.status = 1 AND im.created_date BETWEEN FROM_UNIXTIME(%s) AND FROM_UNIXTIME(%s)
            GROUP BY 
                im.id
            ORDER BY
                im.created_date DESC
            LIMIT 11 OFFSET %s;
        """
        cursor.execute(query, (event['pathParameters']['start-date'], event['pathParameters']['end-date'], offset))
        rows = cursor.fetchall()
        column_names = [column[0] for column in cursor.description]
        transformed_rows = [
            dict(zip(column_names, transform_row(row))) for row in rows]

        response =  create_response(200, '', transformed_rows)
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