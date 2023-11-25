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
    
def lambda_handler(event, context):
    effect = 'Deny'
    return create_policy('Allow', event['methodArn'])
    user_info = get_user_info(event['authorizationToken'])
    admin_permission = ['GET/patient/name', 'ESTestInvoke-stage']
    # doctor_permission = ['POST/appointment ', 'PUT/appointment/' , 'GET/appointment/', 'DELETE/appointment/','GET/timekeeping/','POST/patient', 'PUT/patient/', 'GET/patient/','GET/treatment-course/patient-id/', 'POST/treatment-course', 'PUT/treatment-course/','GET/medical-supply/status/','GET/appointment/','GET/material-usage/report/', 'GET/labo','GET/patient/name/','POST/medical-supply','PUT/medical-supply/','GET/medical-supply/status/','GET/material-usage/report/']
    # receptionist_permission = ['POST/waiting-room', 'GET/waiting-room', 'DELETE/waiting-room/', 'PUT/waiting-room/','GET/timekeeping/','POST/timekeeping','POST/patient', 'PUT/patient/', 'GET/patient/','GET/treatment-course/patient-id/','GET/medical-supply/status/','GET/appointment/','GET/material-usage/report/']
    # head_nurse_permission = ['POST/appointment ', 'PUT/appointment/' , 'GET/appointment/', 'DELETE/appointment/','GET/timekeeping/','POST/patient', 'PUT/patient/', 'GET/patient/','GET/treatment-course/patient-id/', 'POST/treatment-course', 'PUT/treatment-course/','GET/medical-supply/status/','GET/appointment/','GET/material-usage/report/','GET/labo','GET/patient/name/','POST/medical-supply','PUT/medical-supply/','GET/medical-supply/status/','GET/material-usage/report/']
    # nurse_permission = ['POST/appointment ', 'PUT/appointment/' , 'GET/appointment/', 'DELETE/appointment/','GET/timekeeping/','POST/patient', 'PUT/patient/', 'GET/patient/','GET/treatment-course/patient-id/', 'POST/treatment-course', 'PUT/treatment-course/','GET/medical-supply/status/','GET/appointment/','GET/material-usage/report/','GET/labo','GET/patient/name/','POST/medical-supply','PUT/medical-supply/','GET/medical-supply/status/','GET/material-usage/report/','GET/medical-supply/labo/', 'GET/medical-supply/patient/', 'GET/medical-supply/search', 'GET/medical-supply/status/', 'GET/medical-supply/','GET/material-warehouse/remaining/','PUT/material-warehouse/material_warehouse_id/']
    doctor_permission =[]
    receptionist_permission=[]
    head_nurse_permission =[]
    nurse_permission=[]
    if user_info is None:
        return create_policy(effect, event['methodArn'])
    custom_role_value = str(get_value_of_name(user_info['UserAttributes'], 'custom:role'))
    
    if '1' in custom_role_value:
        return create_policy('Allow', event['methodArn'])
    elif '2' in custom_role_value and contains_any(str(event['methodArn']), doctor_permission):
        return create_policy('Allow', event['methodArn'])
    elif '3' in custom_role_value and contains_any(str(event['methodArn']), receptionist_permission):
        return create_policy('Allow', event['methodArn'])
    elif '4' in custom_role_value and contains_any(str(event['methodArn']), head_nurse_permission):
        return create_policy('Allow', event['methodArn'])
    elif '5' in custom_role_value and contains_any(str(event['methodArn']), nurse_permission):
        return create_policy('Allow', event['methodArn'])
    return create_policy(effect, event['methodArn'])
