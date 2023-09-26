import boto3
import json
import os

USER_POOL_ID = os.environ.get('USER_POOL_ID')
CLIENT_ID = os.environ.get('CLIENT_ID')

client = boto3.client('cognito-idp', region_name='ap-southeast-1')


def get_client():
  global client
  if client is None:
    client = boto3.client('cognito-idp', region_name='ap-southeast-1')
  return client


def response(message, error=True, status_code=200):
  return {
      "statusCode": status_code,
      "headers": {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*"
      },
      "body": json.dumps({
          "error": error,
          "success": not error,
          "message": message
      }),
      "isBase64Encoded": False
  }


def handler(event, context):
  body = json.loads(event['body'])
  for field in ["username", "password", "name", "group"]:
    if not body.get(field):
      return response(f"{field} is not present")

  username = body['username']
  password = body['password']
  name = body["name"]
  group = body["group"]
  try:
    get_client().sign_up(
        ClientId=CLIENT_ID,
        Username=username,
        Password=password,
        UserAttributes=[
            {'Name': "name", 'Value': name}
        ]
    )
    get_client().admin_confirm_sign_up(
        UserPoolId=USER_POOL_ID,
        Username=username
    )
    get_client().admin_add_user_to_group(
        UserPoolId=USER_POOL_ID,
        Username=username,
        GroupName=group
    )
  except get_client().exceptions.UsernameExistsException:
    return response("This username already exists")
  except get_client().exceptions.InvalidPasswordException:
    return response("Password should have Caps, Special chars, Numbers")
  except get_client().exceptions.UserLambdaValidationException:
    return response("Email already exists")
  except Exception as e:
    get_client().admin_delete_user(
        UserPoolId=USER_POOL_ID,
        Username=username
    )
    return response(str(e))

  return response("Please confirm your signup", error=False)
