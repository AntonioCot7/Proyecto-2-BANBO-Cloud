import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TABLA-SOPORTE')

def lambda_handler(event, context):
    try:
        # Cargar el cuerpo de la solicitud en caso de que sea un string
        data = json.loads(event['body'])
        
        usuario_id = data['usuario_id']
        ticket_id = data['ticket_id']
        
        # Obtener la solicitud por usuario_id y ticket_id
        response = table.get_item(Key={'usuario_id': usuario_id, 'ticket_id': ticket_id})
        
        if 'Item' in response:
            return {
                'statusCode': 200,
                'body': json.dumps(response['Item'])  # Convertir a JSON para la respuesta
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps('Solicitud no encontrada')  # Convertir mensaje a JSON
            }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error interno del servidor: {str(e)}")
        }
