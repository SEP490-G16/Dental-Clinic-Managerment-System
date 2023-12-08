import json
import pymysql
import os
import datetime
from collections import defaultdict


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
            'id' not in event['pathParameters'] or
            not event['pathParameters']['id'] or
            event['httpMethod'] != 'GET'):
        return create_response(400, 'Bad Request')

    try:
        conn = pymysql.connect(host=os.environ.get('HOST'), user=os.environ.get('USERNAME'),
                               passwd=os.environ.get('PASSWORD'), db=os.environ.get('DATABASE'))
        cursor = conn.cursor()
        query = """
          SELECT 
              mu.material_usage_id AS mu_material_usage_id,
              mu.material_warehouse_id AS mu_material_warehouse_id,
              mu.medical_procedure_id AS mu_medical_procedure_id,
              mu.examination_id AS mu_examination_id,
              mu.quantity AS mu_quantity,
              mu.price AS mu_price,
              mu.total AS mu_total,
              mu.total_paid AS mu_total_paid,
              mu.description AS mu_description,
              mu.status AS mu_status,
              mu.created_date AS mu_created_date,
              tc.treatment_course_id AS tc_treatment_course_id,
              tc.description AS tc_description,
              tc.status AS tc_status,
              tc.created_date AS tc_created_date,
              tc.name AS tc_name,
              p.patient_id AS p_patient_id,
              p.patient_name AS p_patient_name,
              p.date_of_birth AS p_date_of_birth,
              p.gender AS p_gender,
              p.phone_number AS p_phone_number,
              p.full_medical_history AS p_full_medical_history,
              p.dental_medical_history AS p_dental_medical_history,
              p.email AS p_email,
              p.address AS p_address,
              p.description AS p_description,
              p.profile_image AS p_profile_image,
              p.active AS p_active,
              p.created_date AS p_created_date
          FROM 
              material_usage mu
          INNER JOIN 
              treatment_course tc ON mu.treatment_course_id = tc.treatment_course_id
          INNER JOIN 
              patient p ON tc.patient_id = p.patient_id
          WHERE 
              p.patient_id = %s;
        """
        #           mu.status != 0 AND
        #   tc.status = 1 AND
        #   p.active = 1 AND
        cursor.execute(query, (event['pathParameters']['id']))
        rows = cursor.fetchall()
        column_names = [column[0] for column in cursor.description]

        grouped_data = defaultdict(
            lambda: {'mu_data': [], 'tc_data': None, 'p_data': None})
        for row in rows:
            transformed_row = transform_row(row)
            row_dict = dict(zip(column_names, transformed_row))

            # Tạo key dựa trên ngày
            key = row_dict['mu_created_date']

            # Nhóm dữ liệu
            grouped_data[key]['mu_data'].append(
                {k: v for k, v in row_dict.items() if k.startswith('mu_')})
            if 'tc_data' not in grouped_data[key] or grouped_data[key]['tc_data'] is None:
                grouped_data[key]['tc_data'] = {
                    k: v for k, v in row_dict.items() if k.startswith('tc_')}
            if 'p_data' not in grouped_data[key] or grouped_data[key]['p_data'] is None:
                grouped_data[key]['p_data'] = {
                    k: v for k, v in row_dict.items() if k.startswith('p_')}

        transformed_rows = list(grouped_data.values())

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
