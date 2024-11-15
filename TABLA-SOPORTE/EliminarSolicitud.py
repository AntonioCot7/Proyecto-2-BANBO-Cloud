import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TABLA-SOPORTE')

def lambda_handler(event, context):
    data = json.loads(event['body'])
    usuario_id = data['usuario_id']
    ticket_id = data['ticket_id']
    
    table.delete_item(
        Key={
            'usuario_id': usuario_id,
            'ticket_id': ticket_id
        }
    )
    
    return {
        'statusCode': 200,
        'body': f'Solicitud {ticket_id} del usuario {usuario_id} se eliminó correctamente'
    }
