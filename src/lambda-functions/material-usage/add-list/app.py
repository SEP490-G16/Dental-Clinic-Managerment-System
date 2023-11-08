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
    if event['httpMethod'] != 'POST' or not event.get('body'):
        return create_response(400, 'Bad Request')

    data = json.loads(event['body'])

    # material_ids = {}
    # duplicated_material_ids = []

    # for item in data:
    #     material_id = item.get('material_id')
    #     if material_id in material_ids:
    #         duplicated_material_ids.append(material_id)
    #     material_ids[material_id] = True

    # if duplicated_material_ids:
    #     return create_response(400, "Material IDs are duplicated in the request.", duplicated_material_ids)

    # check required
    missing_fields_list = []

    required_fields = ['material_warehouse_id', 'treatment_course_id', 'examination_id', 'quantity', 'price']

    for item in data:
        missing_fields = [field for field in required_fields if field not in item]
        if missing_fields:
            missing_fields_list.append({'examination_id': item.get('examination_id'), 'missing_fields': missing_fields})

    if missing_fields_list:
        missing_materials = ', '.join([f"Examination ID: {item['examination_id']} is missing fields: {', '.join(item['missing_fields'])}" for item in missing_fields_list])
        return create_response(400, f"Missing fields for the following materials: {missing_materials}")

    try:
        conn = pymysql.connect(host=os.environ.get('HOST'), user=os.environ.get('USERNAME'), passwd=os.environ.get('PASSWORD'), db=os.environ.get('DATABASE'))
        conn.autocommit(False)
        cursor = conn.cursor()
        query = """INSERT INTO `material_usage` (`material_warehouse_id`, `treatment_course_id`, `examination_id`, `quantity`, `price`, `total_paid`, `description`) VALUES """
        query_data = ()
        for item in data:
            query += "(%s, %s, %s, %s, %s, FROM_UNIXTIME(%s), %s),"
            query_data += (get_value_or_none(item, 'material_id'), get_value_or_none(item, 'import_material_id'), get_value_or_none(item, 'quantity_import'), get_value_or_none(item, 'quantity_import'), get_value_or_none(item, 'price'), get_value_or_none(item, 'warranty'), get_value_or_none(item, 'discount'))
        cursor.execute(query[:-1], query_data)
        conn.commit()
        response = create_response(201, message='Material insert successfully into warehouse')
    except pymysql.MySQLError as e:
        print("MySQL error:", e)
        error_message = get_mysql_error_message(e.args[0])
        status_code = 400 if e.args[0] in [1452, 1062, 1054] else 500
        response = create_response(status_code, error_message, None, str(e.__class__.__name__))
        if conn:
            conn.rollback()
    except Exception as e:
        print("Error:", e)
        response = create_response(500, 'Internal error', None, str(e.__class__.__name__))
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return response