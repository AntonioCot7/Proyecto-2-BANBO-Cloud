import boto3
import json
from boto3.dynamodb.conditions import Key
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')

def decimal_to_float(item):
    """Recursively convert Decimal types to float in a dictionary or list."""
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
    
    transaccion_table = dynamodb.Table('TABLA-TRANSACCION')
    
    try:
        response = transaccion_table.query(
            KeyConditionExpression=Key('cuenta_origen').eq(cuenta_origen)
        )

        items = decimal_to_float(response.get('Items', []))
        
        return {
            'statusCode': 200,
            'body': json.dumps(items)
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Error al listar transacciones: {str(e)}'})
        }
