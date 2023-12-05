import json
import pymysql
import os
import datetime
import boto3
import base64
from botocore.exceptions import ClientError

s3_client = boto3.client('s3')


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

    required_fields = ['patient_id', 'image_arr']

    missing_fields = [
        field for field in required_fields if not data.get(field)]

    if missing_fields:
        return create_response(400, f"Fields {', '.join(missing_fields)} are required")

    image_arr = data.get('image_arr')

    for item in image_arr:
        if 'x-ray' not in item or not item['x-ray'].strip():
            return create_response(400, "Field 'x-ray' is required")

    query = "INSERT INTO `x_ray_image`(`patient_id`, `url`, `description`) VALUES \n"
    query_data = ()

    count = 0
    for item in image_arr:
        image_url = None
        if item['base64']:
            try:
                count += 1
                image_url_s3 = "{}/{}/{}.jpg".format(
                    data.get('patient_id'), event['requestContext']['requestId'], str(count))
                image_data = base64.b64decode(item['image_data'])
                s3_client.put_object(Body=image_data, Bucket=os.environ.get(
                    'BUCKET_IMAGE_NAME'), Key=image_url_s3, ACL='public-read', ContentType='image/jpeg')
                image_url = "https://{}.s3.{}.amazonaws.com/{}".format(
                    os.environ.get('BUCKET_IMAGE_NAME'), os.environ.get('REGION'), image_url_s3)
            except Exception as e:
                print(str(e))
        else:
            image_url = item['image_url']
        query += "(%s, %s, %s),"
        query_data += (get_value_or_none(data, 'patient_id'),
                       image_url,
                       get_value_or_none(item, 'description'))
    try:
        conn = pymysql.connect(host=os.environ.get('HOST'), user=os.environ.get(
            'USERNAME'), passwd=os.environ.get('PASSWORD'), db=os.environ.get('DATABASE'))
        cursor = conn.cursor()
        cursor.execute(query[:-1], query_data)
        response = create_response(
            201, message='X-ray image created successfully')
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
