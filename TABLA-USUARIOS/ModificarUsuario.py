import boto3
import json
import hashlib
from boto3.dynamodb.conditions import Key

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

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
    updated_data = body
    if not usuario_id or not updated_data:
        return {
            'statusCode': 400,
            'body': 'Solicitud inválida. Faltan usuario_id o datos de actualización.'
        }

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('TABLA-USUARIOS')

    if 'email' in updated_data:
        email_response = table.query(
            IndexName='email-index',
            KeyConditionExpression=Key('email').eq(updated_data['email'])
        )
        if email_response.get('Items'):
            existing_user = email_response['Items'][0]
            if existing_user['usuario_id'] != usuario_id:
                return {
                    'statusCode': 400,
                    'body': 'El email ya está registrado por otro usuario. Por favor, utiliza otro email.'
                }

    if 'dni' in updated_data:
        dni_response = table.query(
            IndexName='dni-index',
            KeyConditionExpression=Key('dni').eq(updated_data['dni'])
        )
        if dni_response.get('Items'):
            existing_user = dni_response['Items'][0]
            if existing_user['usuario_id'] != usuario_id:
                return {
                    'statusCode': 400,
                    'body': 'El DNI ya está registrado por otro usuario. Por favor, utiliza otro DNI.'
                }

    # Construir la expresión de actualización
    update_expression = "set "
    expression_attribute_values = {}
    for key, value in updated_data.items():
        if key != 'usuario_id':
            if key == "password":
                hashed_password = hash_password(value)
                update_expression += f"{key} = :{key}, "
                expression_attribute_values[f":{key}"] = hashed_password
            else:
                update_expression += f"{key} = :{key}, "
                expression_attribute_values[f":{key}"] = value
    update_expression = update_expression.rstrip(", ")

    # Actualizar el usuario
    try:
        response = table.update_item(
            Key={'usuario_id': usuario_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW"
        )

        return {
            'statusCode': 200,
            'body': f'Usuario {usuario_id} modificado exitosamente'
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error al modificar el usuario: {str(e)}'
        }
