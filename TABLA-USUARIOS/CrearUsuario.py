import boto3
import hashlib
import uuid
import json
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token():
    return str(uuid.uuid4())

def get_next_user_id(table):
    response = table.scan(
        ProjectionExpression="usuario_id"
    )
    items = response['Items']
    user_ids = [int(item['usuario_id'].split('-')[1]) for item in items if item['usuario_id'].startswith('CLIENTE-')]
    next_id = max(user_ids) + 1 if user_ids else 1
    return f"CLIENTE-{next_id}"

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    usuarios_table = dynamodb.Table('TABLA-USUARIOS')
    tokens_table = dynamodb.Table('TABLA-TOKENS_ACCESO')

    if isinstance(event.get('body'), str):
        try:
            body = json.loads(event['body'])
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'body': {
                    'message': 'Error en el formato del JSON enviado.'
                }
            }
    else:
        body = event.get('body', event)

    required_keys = ['nombre', 'apellido', 'email', 'telefono', 'dni', 'direccion', 'fecha_nac', 'password']
    missing_keys = [key for key in required_keys if key not in body]
    if missing_keys:
        return {
            'statusCode': 400,
            'body': {
                'message': f'Faltan los siguientes campos requeridos: {", ".join(missing_keys)}.'
            }
        }

    email_response = usuarios_table.query(
        IndexName='email-index',  # Nombre del índice secundario global para email
        KeyConditionExpression=Key('email').eq(body['email'])
    )
    
    if email_response.get('Items'):
        return {
            'statusCode': 400,
            'body': {
                'message': 'El email ya está registrado. Por favor, utiliza otro email.'
            }
        }

    dni_response = usuarios_table.query(
        IndexName='dni-index',  # Nombre del índice secundario global para dni
        KeyConditionExpression=Key('dni').eq(body['dni'])
    )
    
    if dni_response.get('Items'):
        return {
            'statusCode': 400,
            'body': {
                'message': 'El DNI ya está registrado. Por favor, utiliza otro DNI.'
            }
        }

    usuario_id = get_next_user_id(usuarios_table)
    hashed_password = hash_password(body['password'])

    usuarios_table.put_item(
        Item={
            'usuario_id': usuario_id,
            'nombre': body['nombre'],
            'apellido': body['apellido'],
            'email': body['email'],
            'telefono': body['telefono'],
            'dni': body['dni'],
            'direccion': body['direccion'],
            'fecha_nac': body['fecha_nac'],
            'password': hashed_password
        }
    )

    token = generate_token()
    expires = (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
    
    tokens_table.put_item(
        Item={
            'token': token,
            'expires': expires,
            'usuario_id': usuario_id
        }
    )

    return {
        'statusCode': 200,
        'body': {
            'message': 'Usuario creado exitosamente',
            'usuario_id': usuario_id,
            'token': token,
            'expires': expires
        }
    }
