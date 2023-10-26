import json
import pymysql
import os
import datetime

conn = pymysql.connect(host=os.environ.get('HOST'),
                       user=os.environ.get('USERNAME'),
                       passwd=os.environ.get('PASSWORD'),
                       db=os.environ.get('DATABASE'))
cursor = conn.cursor()


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


def lambda_handler(event, context):
    global conn, cursor

    if event['httpMethod'] != 'DELETE':
        return {
            'statusCode': 400,
            'headers': {},
            'body': json.dumps({'message': 'Bad Request'})
        }

    treatment_course_id = event['pathParameters']['treatment_course_id']

    try:
        query = """
        UPDATE `treatment_course`
        SET 
        `status` = 0
        WHERE `treatment_course_id` = %s;
        """

        cursor.execute(query, (treatment_course_id,))

        if cursor.rowcount == 0:
            return {
                'statusCode': 404,
                'headers': {},
                'body': json.dumps({'message': 'Treatment course not found'})
            }

        conn.commit()

        return {
            'statusCode': 200,
            'headers': {},
            'body': json.dumps({'message': 'Treatment course deactivated successfully'})
        }
    except pymysql.MySQLError as e:
        print("MySQL error:", e)
        error_message = get_mysql_error_message(e.args[0])
        return {
            'statusCode': 400 if e.args[0] in [1452, 1062, 1054] else 500,
            'headers': {},
            'body': json.dumps({'message': error_message, 'type': str(e.__class__.__name__)})
        }
    except Exception as e:
        print("Error:", e)
        return {
            'statusCode': 500,
            'headers': {},
            'body': json.dumps({'message': 'Internal error', 'type': str(e.__class__.__name__)})
        }
