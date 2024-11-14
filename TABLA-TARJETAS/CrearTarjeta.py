import boto3
import json
from datetime import datetime
from decimal import Decimal
import random

def generate_card_number():
    """Genera un número de tarjeta de 16 dígitos en formato xxxx-xxxx-xxxx-xxxx"""
    return '-'.join([''.join([str(random.randint(0, 9)) for _ in range(4)]) for _ in range(4)])

def lambda_handler(event, context):
    if isinstance(event['body'], str):
        body = json.loads(event['body'])
    else:
        body = event['body']

    usuario_id = body.get('usuario_id')
    cuenta_id = body.get('cuenta_id')
    tarjeta_datos = body.get('tarjeta_datos', {})

    dynamodb = boto3.resource('dynamodb')
    usuarios_table = dynamodb.Table('TABLA-USUARIOS')
    cuentas_table = dynamodb.Table('TABLA-CUENTA')
    tarjetas_table = dynamodb.Table('TABLA-TARJETAS')

    user_response = usuarios_table.get_item(Key={'usuario_id': usuario_id})
    if 'Item' not in user_response:
        return {
            'statusCode': 400,
            'body': 'Error: Usuario no encontrado.'
        }

    cuenta_response = cuentas_table.get_item(Key={'usuario_id': usuario_id, 'cuenta_id': cuenta_id})
    if 'Item' not in cuenta_response:
        return {
            'statusCode': 400,
            'body': 'Error: Cuenta no encontrada para este usuario.'
        }

    estado = tarjeta_datos.get('estado', 'activa')
    if estado not in ['activa', 'bloqueada']:
        return {
            'statusCode': 400,
            'body': 'Error: Estado inválido. Solo se permite activa o bloqueada.'
        }

    tarjeta_id = generate_card_number()
    while True:
        existing_card = tarjetas_table.query(
            IndexName='tarjeta_id-index',
            KeyConditionExpression=boto3.dynamodb.conditions.Key('tarjeta_id').eq(tarjeta_id)
        )
        if existing_card['Count'] == 0:
            break
        tarjeta_id = generate_card_number()

    tarjeta_item = {
        'cuenta_id': cuenta_id,
        'tarjeta_id': tarjeta_id,
        'saldo_disponible': Decimal('0.00'),
        'estado': estado,
        'fecha_emision': datetime.now().strftime('%Y-%m-%d'),
        'fecha_vencimiento': (datetime.now().replace(year=datetime.now().year + 3)).strftime('%Y-%m-%d'),
        'cvv': str(datetime.now().microsecond % 1000).zfill(3)
    }

    tarjetas_table.put_item(Item=tarjeta_item)

    return {
        'statusCode': 200,
        'body': f'Tarjeta creada exitosamente con ID: {tarjeta_id}'
    }
