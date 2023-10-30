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
            'headers': {},
            'body': json.dumps({'message': 'Bad Request'})
        }

    try:
        id = event['pathParameters']['id']

        # Cập nhật trường `active` của bản ghi patient thành 0
        query = "UPDATE `medical_procedure_group` SET `active`=0 WHERE patient_id=%s;"

        cursor.execute(query, (id))

        conn.commit()

        if cursor.rowcount == 0:  # Nếu không có bản ghi nào được cập nhật
            return {
                'statusCode': 404,
                'headers': {},
                'body': json.dumps({'message': 'medical procedure group not found'})
            }

        return {
            'statusCode': 200,
            'headers': {},
            'body': json.dumps({'message': 'medical procedure group deactivated successfully'})
        }
    except pymysql.MySQLError as e:
        print("MySQL error:", e)
        return {
            'statusCode': 500,
            'headers': {},
            'body': json.dumps({'message': 'Database error', 'type': str(e.__class__.__name__)})
        }
    except Exception as e:
        print("Error:", e)
        return {
            'statusCode': 500,
            'headers': {},
            'body': json.dumps({'message': 'Internal error', 'type': str(e.__class__.__name__)})
        }
