import boto3
import json
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TABLA-SOPORTE')

def lambda_handler(event, context):
    try:
        # Cargar el cuerpo del evento como JSON
        data = json.loads(event['body'])
        usuario_id = data['usuario_id']
        ticket_id = data['ticket_id']
        response_text = data['response']
        
        # Obtener el ítem actual de DynamoDB
        response = table.get_item(Key={'usuario_id': usuario_id, 'ticket_id': ticket_id})
        
        # Verificar si la solicitud ya fue respondida
        if response.get('Item', {}).get('estado') == 'respondido':
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'La solicitud ya fue respondida.'})
            }
        
        # Preparar la actualización con la respuesta y la fecha actual
        fecha_respuesta = datetime.utcnow().isoformat()
        table.update_item(
            Key={'usuario_id': usuario_id, 'ticket_id': ticket_id},
            UpdateExpression="SET #resp = :response_text, estado = :estado, fecha_respuesta = :fecha",
            ExpressionAttributeNames={
                '#resp': 'response'  # Alias para el atributo 'response'
            },
            ExpressionAttributeValues={
                ':response_text': response_text,
                ':estado': 'respondido',
                ':fecha': fecha_respuesta
            }
        )
        
        # Retornar la respuesta confirmando la actualización
        return {
            'statusCode': 200,
            'body': json.dumps({
                'usuario_id': usuario_id,
                'ticket_id': ticket_id,
                'response': response_text,
                'estado': 'respondido',
                'fecha_respuesta': fecha_respuesta
            })
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f"Error interno del servidor: {str(e)}"})
        }
