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
    if (event['httpMethod'] != 'GET'):
        return create_response(400, 'Bad Request')

    try:
        query_params = event.get('queryStringParameters', {})
        if query_params['paging'] == '':
            return create_response(400, 'Fields paging are required')
        conn = pymysql.connect(host=os.environ.get('HOST'), user=os.environ.get('USERNAME'),
                               passwd=os.environ.get('PASSWORD'), db=os.environ.get('DATABASE'))
        cursor = conn.cursor()

        query = """
            SELECT ms.*, p.patient_name FROM `medical_supply` ms 
            LEFT JOIN `patient` p ON ms.patient_id = p.patient_id
        """
        query_data = ()
        status = query_params.get('status')
        if status and status.isdigit():
            status = int(status)
            if status in [1, 2, 3, 4]:
                query += " WHERE status = %s"
                query_data += (status,)
            else:
                query += " WHERE status != 0 AND status != 1"
        else:
            query += " WHERE status != 0 AND status != 1"

        if query_params['labo_id'] != '':
            query += """
              AND `labo_id` = %s
            """
            query_data += (query_params['labo_id'],)

        if query_params['order_date_start'] != '' and query_params['order_date_end'] != '':
            query += """
              AND `order_date` BETWEEN FROM_UNIXTIME(%s) AND FROM_UNIXTIME(%s)
            """
            query_data += (query_params['order_date_start'],
                           query_params['order_date_end'])

        if query_params['received_date_start'] != '' and query_params['received_date_end'] != '':
            query += """
              AND `received_date` BETWEEN FROM_UNIXTIME(%s) AND FROM_UNIXTIME(%s)
            """
            query_data += (query_params['received_date_start'],
                           query_params['received_date_end'])

        if query_params['used_date_start'] != '' and query_params['used_date_end'] != '':
            query += """
              AND `used_date` BETWEEN FROM_UNIXTIME(%s) AND FROM_UNIXTIME(%s)
            """
            query_data += (query_params['used_date_start'],
                           query_params['used_date_end'])

        query += """
            ORDER BY `order_date` DESC
            LIMIT 11 OFFSET %s
        """

        offset = (int(query_params['paging']) - 1) * 10
        query_data += (offset,)
        cursor.execute(query, query_data)
        rows = cursor.fetchall()
        column_names = [column[0] for column in cursor.description]
        transformed_rows = [
            dict(zip(column_names, transform_row(row))) for row in rows]

        response = create_response(200, '', transformed_rows)
    except pymysql.MySQLError as e:
        print("MySQL error:", e)
        error_message = get_mysql_error_message(e.args[0])
        status_code = 400 if e.args[0] in [1452, 1062, 1054] else 500
        response = create_response(
            status_code, error_message, None, str(e.__class__.__name__))
    except Exception as e:
        print("Error:", e)
        response = create_response(
            500, 'Internal error', None, str(e.__class__.__name__))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return response
