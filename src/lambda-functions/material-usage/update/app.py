import json
import pymysql
import os
import datetime


def get_value_or_none(data, key):
    return data[key] if key in data else None


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

    if event['httpMethod'] != 'PUT' or not event.get('body') or not event.get('pathParameters') or 'id' not in event['pathParameters']:
        return create_response(400, 'Bad Request')

    try:
        id = event['pathParameters']['id']
        data = json.loads(event['body'])

        if (data.get('medical_procedure_id') is None and data.get('material_warehouse_id') is None) or (data.get('medical_procedure_id') is not None and data.get('material_warehouse_id') is not None):
            return create_response(400, 'Must has one of material_warehouse_id or medical_procedure_id')
        required_fields = ['treatment_course_id', 'quantity', 'price']

        missing_fields = [
            field for field in required_fields if not data.get(field)]

        if missing_fields:
            return create_response(400, f"Fields {', '.join(missing_fields)} are required")
        conn = pymysql.connect(host=os.environ.get('HOST'), user=os.environ.get(
            'USERNAME'), passwd=os.environ.get('PASSWORD'), db=os.environ.get('DATABASE'))
        cursor = conn.cursor()
        query = """
            UPDATE `material_usage` 
            SET `material_warehouse_id` = %s, `medical_procedure_id` = %s, `treatment_course_id` = %s, `examination_id` = %s, `quantity` = %s, `price` = %s, `description` = %s
            WHERE material_usage_id=%s;
            """
        cursor.execute(query, (get_value_or_none(data, 'material_warehouse_id'),
                               get_value_or_none(data, 'medical_procedure_id'),
                               get_value_or_none(data, 'treatment_course_id'),
                               get_value_or_none(data, 'examination_id'),
                               get_value_or_none(data, 'quantity'),
                               get_value_or_none(data, 'price'),
                               get_value_or_none(data, 'description'),
                               id))

        conn.commit()
        if cursor.rowcount == 0:
            response = create_response(
                status_code=404, message='Material usage not found or not change')
        else:
            response = create_response(
                status_code=200, message='Material usage updated successfully')
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
