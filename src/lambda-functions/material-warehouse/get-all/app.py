import json
import pymysql
import os
import datetime
import decimal

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
            'paging' not in event['pathParameters'] or
            not event['pathParameters']['paging'] or
            event['httpMethod'] != 'GET'):
        return create_response(400, 'Bad Request')
    try:
        page_number = int(event['pathParameters']['paging'])
        offset = (page_number - 1) * 10
    except ValueError:
        return create_response(400, 'Invalid paging value')
    
    try:
        conn = pymysql.connect(host=os.environ.get('HOST'), user=os.environ.get('USERNAME'),
                       passwd=os.environ.get('PASSWORD'), db=os.environ.get('DATABASE'))
        cursor = conn.cursor()
        query = """
            SELECT 
                mw.material_warehouse_id AS mw_material_warehouse_id,
                mw.import_material_id AS mw_import_material_id,
                mw.quantity_import AS mw_quantity_import,
                mw.remaining AS mw_remaining,
                mw.price AS mw_price,
                mw.warranty AS mw_warranty,
                mw.discount AS mw_discount,
                m.material_id AS m_material_id,
                m.material_name AS m_material_name,
                m.unit AS m_unit
            FROM 
                material_warehouse mw
                INNER JOIN (
                    SELECT 
                    	material_id
                    FROM 
                    	material_warehouse
                    GROUP BY 
                    	material_id
                    ORDER BY 
                    	material_id
                    LIMIT 11 OFFSET %s
                ) as subquery
                ON mw.`material_id` = subquery.`material_id`
            LEFT JOIN `material` m on mw.material_id = m.material_id
            WHERE mw.status != 0 AND mw.remaining > 0 AND m.status = 1
        """
        cursor.execute(query, (offset))
        rows = cursor.fetchall()
        column_names = [column[0] for column in cursor.description]
        transformed_rows = [
            dict(zip(column_names, transform_row(row))) for row in rows]
        response = create_response(200, '', transformed_rows)
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