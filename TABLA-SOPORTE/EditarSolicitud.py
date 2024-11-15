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
        solicitud_anterior = response['Item']  # Guardar los datos originales antes de modificar
        estado_actual = solicitud_anterior.get('estado', 'pendiente')
        
        # Verificar si la solicitud ya ha sido respondida
        if estado_actual == 'respondido':
            # Retornar el mensaje de error junto con los detalles de la solicitud original
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'mensaje': 'La solicitud ya fue respondida y no puede ser modificada.',
                    'titulo': solicitud_anterior.get('Titulo', 'No disponible'),
                    'descripcion': solicitud_anterior.get('descripcion', 'No disponible'),
                    'respuesta': solicitud_anterior.get('respuesta', 'No disponible')
                })
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
        
        # Crear el JSON de la solicitud actualizada
        solicitud_modificada = {
            'momento': 'actual modificado',
            'usuario_id': usuario_id,
            'ticket_id': ticket_id,
            'Titulo': titulo,
            'descripcion': descripcion,
            'estado': 'pendiente',
            'fecha': fecha_actualizacion
        }

        # Crear el JSON de la solicitud anterior
        solicitud_anterior_json = {
            'momento': 'anterior',
            'usuario_id': solicitud_anterior['usuario_id'],
            'ticket_id': solicitud_anterior['ticket_id'],
            'Titulo': solicitud_anterior['Titulo'],
            'descripcion': solicitud_anterior['descripcion'],
            'estado': solicitud_anterior['estado'],
            'fecha': solicitud_anterior['fecha']
        }

        # Retornar ambos JSON en la respuesta
        return {
            'statusCode': 200,
            'body': json.dumps({
                'solicitud_anterior': solicitud_anterior_json,
                'solicitud_modificada': solicitud_modificada
            })
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error interno del servidor: {str(e)}")
        }
