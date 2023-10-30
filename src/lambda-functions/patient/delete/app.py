import json
import pymysql
import os

conn = pymysql.connect(host=os.environ.get('HOST'),
                       user=os.environ.get('USERNAME'),
                       passwd=os.environ.get('PASSWORD'),
                       db=os.environ.get('DATABASE'))
cursor = conn.cursor()


def lambda_handler(event, context):
    global conn, cursor

    # Kiểm tra HTTP method và pathParameters
    if event['httpMethod'] != 'DELETE' or not event.get('pathParameters') or 'id' not in event['pathParameters']:
        return {
            'statusCode': 400,
            'headers': {
                "Access-Control-Allow-Headers": "Access-Control-Allow-Headers, Access-Control-Allow-Methods, Accept, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers, Authorization",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "POST, PUT, PATCH, GET, DELETE, OPTIONS"
            },
            'body': json.dumps({'message': 'Bad Request'})
        }

    try:
        patient_id = event['pathParameters']['id']

        # Cập nhật trường `active` của bản ghi patient thành 0
        query = "UPDATE `patient` SET `active`=0 WHERE patient_id=%s;"

        cursor.execute(query, (patient_id,))

        conn.commit()

        if cursor.rowcount == 0:  # Nếu không có bản ghi nào được cập nhật
            return {
                'statusCode': 404,
                'headers': {
                    "Access-Control-Allow-Headers": "Access-Control-Allow-Headers, Access-Control-Allow-Methods, Accept, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers, Authorization",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Allow-Methods": "POST, PUT, PATCH, GET, DELETE, OPTIONS"
                },
                'body': json.dumps({'message': 'Patient not found'})
            }

        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Headers": "Access-Control-Allow-Headers, Access-Control-Allow-Methods, Accept, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers, Authorization",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "POST, PUT, PATCH, GET, DELETE, OPTIONS"
            },
            'body': json.dumps({'message': 'Patient deactivated successfully'})
        }
    except pymysql.MySQLError as e:
        print("MySQL error:", e)
        return {
            'statusCode': 500,
            'headers': {
                "Access-Control-Allow-Headers": "Access-Control-Allow-Headers, Access-Control-Allow-Methods, Accept, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers, Authorization",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "POST, PUT, PATCH, GET, DELETE, OPTIONS"
            },
            'body': json.dumps({'message': 'Database error', 'type': str(e.__class__.__name__)})
        }
    except Exception as e:
        print("Error:", e)
        return {
            'statusCode': 500,
            'headers': {
                "Access-Control-Allow-Headers": "Access-Control-Allow-Headers, Access-Control-Allow-Methods, Accept, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers, Authorization",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Allow-Methods": "POST, PUT, PATCH, GET, DELETE, OPTIONS"
            },
            'body': json.dumps({'message': 'Internal error', 'type': str(e.__class__.__name__)})
        }
