import boto3
import json
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')

def decimal_to_float(item):
    """Convierte recursivamente objetos Decimal a float en un diccionario o lista."""
    if isinstance(item, list):
        return [decimal_to_float(i) for i in item]
    elif isinstance(item, dict):
        return {k: decimal_to_float(v) for k, v in item.items()}
    elif isinstance(item, Decimal):
        return float(item)
    else:
        return item

def lambda_handler(event, context):
    data = json.loads(event['body'])
    cuenta_origen = data['cuenta_origen']
    transaccion_id = data['transaccion_id']
    
    transaccion_table = dynamodb.Table('TABLA-TRANSACCION')
    
    try:
        response = transaccion_table.get_item(
            Key={
                'cuenta_origen': cuenta_origen,
                'transaccion_id': transaccion_id
            }
        )
        
        if 'Item' in response:
            item = decimal_to_float(response['Item'])
            return {
                'statusCode': 200,
                'body': json.dumps(item)
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Transacción no encontrada'})
            }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Error al obtener la transacción: {str(e)}'})
        }
