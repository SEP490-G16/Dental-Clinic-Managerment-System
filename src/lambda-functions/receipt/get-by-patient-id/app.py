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
                r.receipt_id AS r_receipt_id,
                r.created_date AS r_created_date,
                r.patient_id AS r_patient_id,
                r.payment_type AS r_payment_type,
                p.paid_material_usage_id AS p_paid_material_usage_id,
                p.material_usage_id AS p_material_usage_id,
                p.total_paid AS p_total_paid,
                mu.quantity AS mu_quantity,
                mu.price AS mu_price,
                mu.total AS mu_total,
                mu.material_warehouse_id AS mw_material_warehouse_id,
                m.material_name AS m_material_name,
                mu.medical_procedure_id AS mp_medical_procedure_id,
                mp.name AS mp_name
            FROM receipt r
            JOIN paid_material_usage p ON r.receipt_id = p.receipt_id
            JOIN material_usage mu ON p.material_usage_id = mu.material_usage_id
            LEFT JOIN material_warehouse mw ON mu.material_warehouse_id = mw.material_warehouse_id 
            LEFT JOIN medical_procedure mp ON mu.medical_procedure_id = mp.medical_procedure_id
            LEFT JOIN material m ON mw.material_id = m.material_id
            WHERE r.patient_id = %s
        """
        cursor.execute(query, (event['pathParameters']['id']))
        rows = cursor.fetchall()
        column_names = [column[0] for column in cursor.description]
        transformed_rows = [
            dict(zip(column_names, transform_row(row))) for row in rows]

        result = []
        for record in transformed_rows:
            r_receipt_id = record["r_receipt_id"]
            r_created_date = record["r_created_date"]
            r_patient_id = record["r_patient_id"]
            r_payment_type = record["r_payment_type"]
            detail = {k: v for k, v in record.items() if not k.startswith("r_")}

            existing_record = next(
                (item for item in result if item["r_receipt_id"] == r_receipt_id), None)
            if existing_record:
                existing_record["detail"].append(detail)
            else:
                result.append({"r_receipt_id": r_receipt_id,
                               "r_created_date": r_created_date,
                               "r_patient_id": r_patient_id,
                               "r_payment_type": r_payment_type,
                               "detail": [detail]})

        response = create_response(200, '', result)
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
