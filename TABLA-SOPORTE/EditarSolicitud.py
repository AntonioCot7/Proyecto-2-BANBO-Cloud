import boto3
import uuid
from datetime import datetime
import json
import os

# Obtener referencia a la tabla DynamoDB usando una variable de entorno
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['SOPORTE_TABLE'])

def lambda_handler(event, context):
    try:
        # Cargar el cuerpo de la solicitud, convirtiéndolo a JSON si es una cadena
        data = json.loads(event['body'])
        
        usuario_id = data['usuario_id']
        ticket_id = data['ticket_id']
        titulo = data['Titulo']
        descripcion = data['descripcion']
        
        # Obtener el ítem actual de la solicitud para verificar el estado
        response = table.get_item(Key={'usuario_id': usuario_id, 'ticket_id': ticket_id})
        
        # Verificar si la solicitud existe
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps("Solicitud no encontrada")
            }

        # Obtener el estado actual de la solicitud
        solicitud = response['Item']
        estado_actual = solicitud.get('estado', 'pendiente')
        
        # Verificar si la solicitud ya ha sido respondida
        if estado_actual == 'respondido':
            return {
                'statusCode': 400,
                'body': json.dumps("La solicitud ya fue respondida y no puede ser modificada.")
            }
        
        # Actualizar la solicitud si está en estado "pendiente"
        fecha_actualizacion = datetime.utcnow().isoformat()
        
        table.update_item(
            Key={'usuario_id': usuario_id, 'ticket_id': ticket_id},
            UpdateExpression="SET Titulo = :titulo, descripcion = :descripcion, fecha = :fecha",
            ExpressionAttributeValues={
                ':titulo': titulo,
                ':descripcion': descripcion,
                ':fecha': fecha_actualizacion
            }
        )
        
        # Retornar la solicitud actualizada
        return {
            'statusCode': 200,
            'body': json.dumps({
                'momento': 'actual modificado',
                'usuario_id': usuario_id,
                'ticket_id': ticket_id,
                'Titulo': titulo,
                'descripcion': descripcion,
                'estado': 'pendiente',
                'fecha': fecha_actualizacion
            })
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error interno del servidor: {str(e)}")
        }
