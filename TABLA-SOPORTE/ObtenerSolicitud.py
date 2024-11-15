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
        titulo = data['Titulo']
        descripcion = data['descripcion']
        
        # Obtener la solicitud y verificar si ya ha sido respondida
        response = table.get_item(Key={'usuario_id': usuario_id, 'ticket_id': ticket_id})
        
        if response.get('Item', {}).get('estado') == 'respondido':
            return {
                'statusCode': 400,
                'body': json.dumps('La solicitud ya fue respondida y no puede ser modificada.')
            }

        # Actualizar la solicitud
        table.update_item(
            Key={'usuario_id': usuario_id, 'ticket_id': ticket_id},
            UpdateExpression="SET Titulo = :titulo, descripcion = :descripcion",
            ExpressionAttributeValues={
                ':titulo': titulo,
                ':descripcion': descripcion
            }
        )
        
        # Responder con los detalles de la solicitud actualizada
        return {
            'statusCode': 200,
            'body': json.dumps({
                'momento': 'actual modificado',
                'usuario_id': usuario_id,
                'ticket_id': ticket_id,
                'Titulo': titulo,
                'descripcion': descripcion,
                'estado': 'pendiente'
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error interno del servidor: {str(e)}")
        }
