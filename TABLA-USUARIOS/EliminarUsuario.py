import boto3
import json

def lambda_handler(event, context):
    body = event.get('body')
    if body is None:
        body = event
    elif isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'body': 'Solicitud inválida. El formato del JSON es incorrecto.'
            }

    usuario_id = body.get('usuario_id')
    if not usuario_id:
        return {
            'statusCode': 400,
            'body': 'Solicitud inválida. Falta el campo usuario_id.'
        }

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('TABLA-USUARIOS')
    
    existing_user = table.get_item(Key={'usuario_id': usuario_id})
    if 'Item' not in existing_user:
        return {
            'statusCode': 404,
            'body': f'Usuario {usuario_id} no existe o ya fue eliminado.'
        }

    table.delete_item(Key={'usuario_id': usuario_id})

    return {
        'statusCode': 200,
        'body': f'Usuario {usuario_id} eliminado exitosamente'
    }
