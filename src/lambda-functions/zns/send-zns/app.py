import json
import urllib3


def contains_any(main_string, string_list):
    for item in string_list:
        if item in main_string:
            return True
    return False


def get_value_of_name(attributes, name):
    for attribute in attributes:
        if attribute['Name'] == name:
            return attribute['Value']
    return None


def get_user_info(access_token):
    http = urllib3.PoolManager()

    url = 'https://cognito-idp.ap-southeast-1.amazonaws.com/'
    headers = {
        'Content-Type': 'application/x-amz-json-1.1',
        'X-Amz-Target': 'AWSCognitoIdentityProviderService.GetUser'
    }

    data = {
        'AccessToken': access_token
    }

    encoded_data = json.dumps(data).encode('utf-8')

    response = http.request('POST', url, body=encoded_data, headers=headers)

    if response.status == 200:
        return json.loads(response.data.decode('utf-8'))
    else:
        return None


def create_policy(effect, resource):
    return {
        'principalId': 'user',
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': effect,
                    'Resource': resource
                }
            ]
        }
    }


def get_access_token():
    return


def send_zns():
    return


def lambda_handler(event, context):
    effect = 'Deny'
    return create_policy('Allow', event['methodArn'])
