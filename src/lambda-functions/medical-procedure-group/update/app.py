import json
import pymysql
import os

conn = pymysql.connect(host=os.environ.get('HOST'),
                       user=os.environ.get('USERNAME'),
                       passwd=os.environ.get('PASSWORD'),
                       db=os.environ.get('DATABASE'))
cursor = conn.cursor()


def get_value_or_none(data, key):
    return data[key] if key in data else None


def lambda_handler(event, context):
    global conn, cursor

    if event['httpMethod'] != 'PUT' or not event.get('body') or not event.get('pathParameters') or 'id' not in event['pathParameters']:
        return {
            'statusCode': 400,
            'headers': {},
            'body': json.dumps({'message': 'Bad Request'})
        }

    try:
        data = json.loads(event['body'])
        id = event['pathParameters']['id']

        if data.get('name') is None:
            return {
                'statusCode': 400,
                'headers': {},
                'body': json.dumps({'message': 'name fields cannot be set to None'})
            }

        query = """
        UPDATE `medical_procedure_group` 
        SET name=%s, description=%s
        WHERE medical_procedure_group_id=%s;
        """

        cursor.execute(query, (data.get('name'),
                               get_value_or_none(data, 'description'),
                               id))

        conn.commit()

        if cursor.rowcount == 0:
            return {
                'statusCode': 404,
                'headers': {},
                'body': json.dumps({'message': 'medical procedure group not found'})
            }

        return {
            'statusCode': 200,
            'headers': {},
            'body': json.dumps({'message': 'medical procedure group updated successfully'})
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
