import os
import json
import boto3

USER_POOL_ID = os.environ.get('USER_POOL_ID')
CLIENT_ID = os.environ.get('CLIENT_ID')

client = boto3.client('cognito-idp', region_name='ap-southeast-1')


def get_client():
  global client
  if client is None:
    client = boto3.client('cognito-idp', region_name='ap-southeast-1')
  return client


def response(message, error=True, data=None, status_code=200):
  return {
      "statusCode": status_code,
      "headers": {
          "Content-Type": "application/json"
      },
      "body": json.dumps({
          "error": error,
          "success": not error,
          "message": message,
          "data": data
      })
  }


def initiate_auth(username, password):
  try:
    resp = get_client().admin_initiate_auth(
        UserPoolId=USER_POOL_ID,
        ClientId=CLIENT_ID,
        AuthFlow='ADMIN_NO_SRP_AUTH',
        AuthParameters={
            'USERNAME': username,
            'PASSWORD': password,
        },
        ClientMetadata={
            'username': username,
            'password': password,
        })
  except get_client().exceptions.NotAuthorizedException:
    return None, "The username or password is incorrect"
  except get_client().exceptions.UserNotConfirmedException:
    return None, "User is not confirmed"
  except Exception as e:
    return None, e.__str__()
  return resp, None


def handler(event, context):
  body = json.loads(event['body'])
  for field in ["username", "password"]:
    if body.get(field) is None:
      return response(f"{field} is required", status_code=400)

  resp, msg = initiate_auth(body.get(
      'username'), body.get('password'))

  if msg:
    return response(msg, status_code=400)

  if resp.get("AuthenticationResult"):
    return response("success", error=False, data={
        "id_token": resp["AuthenticationResult"]["IdToken"],
        "refresh_token": resp["AuthenticationResult"]["RefreshToken"],
        "access_token": resp["AuthenticationResult"]["AccessToken"],
        "expires_in": resp["AuthenticationResult"]["ExpiresIn"],
        "token_type": resp["AuthenticationResult"]["TokenType"]
    })
  else:  # this code block is relevant only when MFA is enabled
    return response("Multi-factor authentication required", status_code=401)
