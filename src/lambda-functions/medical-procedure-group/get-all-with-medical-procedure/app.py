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
    conn = pymysql.connect(host=os.environ.get('HOST'), user=os.environ.get(
        'USERNAME'), passwd=os.environ.get('PASSWORD'), db=os.environ.get('DATABASE'))
    cursor = conn.cursor()
    try:
        query = """
            SELECT 
                mg.medical_procedure_group_id AS mg_id,
                mg.name AS mg_name,
                mg.description AS mg_description,
                mp.medical_procedure_id AS mp_id,
                mp.name AS mp_name,
                mp.price AS mp_price,
                mp.description AS mp_description,
                mp.active AS mp_active
            FROM medical_procedure_group mg
            INNER JOIN medical_procedure mp ON mg.medical_procedure_group_id = mp.medical_procedure_group_id
            WHERE mg.active != 0 AND mp.active != 0
            UNION
            SELECT 
                mg.medical_procedure_group_id AS mg_id,
                mg.name AS mg_name,
                mg.description AS mg_description,
                NULL AS mp_id,
                NULL AS mp_name,
                NULL AS mp_price,
                NULL AS mp_description,
                NULL AS mp_active
            FROM medical_procedure_group mg
            WHERE mg.active != 0
                AND mg.medical_procedure_group_id NOT IN (
                    SELECT DISTINCT medical_procedure_group_id
                    FROM medical_procedure
                    WHERE (active != 0)
                );
          """
        cursor.execute(query)
        rows = cursor.fetchall()
        column_names = [column[0] for column in cursor.description]
        transformed_rows = [
            dict(zip(column_names, transform_row(row))) for row in rows]

        if len(transformed_rows) == 0:
            return create_response(404, 'Medical procedure group not found')

        return create_response(200, '', transformed_rows)
    except pymysql.MySQLError as e:
        print("MySQL error:", e)
        error_message = get_mysql_error_message(e.args[0])
        status_code = 400 if e.args[0] in [1452, 1062, 1054] else 500
        return create_response(status_code, error_message, None, str(e.__class__.__name__))
    except Exception as e:
        print("Error:", e)
        return create_response(500, 'Internal error', None, str(e.__class__.__name__))
