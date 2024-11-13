import boto3
import json

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    data = json.loads(event['body'])
    usuario_origen = data['usuario_origen']
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

        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Transacción no encontrada'})
            }

        transaccion_table.delete_item(
            Key={
                'cuenta_origen': cuenta_origen,
                'transaccion_id': transaccion_id
            }
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': f'Transacción {transaccion_id} eliminada con éxito'})
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Error al eliminar la transacción: {str(e)}'})
        }
