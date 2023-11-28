def lambda_handler(event, context):
    event['response'] = {
        'autoConfirmUser': True
    }

    return event
