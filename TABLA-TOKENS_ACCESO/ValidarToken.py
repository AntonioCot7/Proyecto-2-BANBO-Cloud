import boto3
from datetime import datetime
import json

def lambda_handler(event, context):
    body = event.get('body')
    if body is None:
        return {'statusCode': 400, 'body': 'Solicitud inválida. Falta el cuerpo de la solicitud.'}

    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            return {'statusCode': 400, 'body': 'El formato del JSON es incorrecto.'}

    token = body.get('token')
    if not token:
        return {'statusCode': 400, 'body': 'Solicitud inválida. Falta el campo "token".'}
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('TABLA-TOKENS_ACCESO')

    response = table.get_item(Key={'token': token})

    if 'Item' not in response:
        return {'statusCode': 403, 'body': 'Token no existe'}
    
    expires = response['Item']['expires']
    if datetime.now().strftime('%Y-%m-%d %H:%M:%S') > expires:
        return {'statusCode': 403, 'body': 'Token expirado'}

    return {
        'statusCode': 200,
        'body': {
            'usuario_id': response['Item']['usuario_id']
        }
    }
