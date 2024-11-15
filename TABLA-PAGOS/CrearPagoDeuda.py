import boto3
import uuid
from datetime import datetime
import json
import os

# DynamoDB setup
dynamodb = boto3.resource('dynamodb')
pagos_table = dynamodb.Table(os.environ['PAGOS_TABLE'])

def lambda_handler(event, context):
    try:
        # Cargar el cuerpo de la solicitud
        data = json.loads(event['body'])

        # Validar campos requeridos
        required_fields = ['usuario_id', 'datos_pago']
        for field in required_fields:
            if field not in data:
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'error': f"El campo {field} es obligatorio"
                    })
                }
        
        datos_pago = data['datos_pago']
        if not all(k in datos_pago for k in ['monto', 'titulo', 'descripcion']):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': "Los campos 'monto', 'titulo' y 'descripcion' son obligatorios en 'datos_pago'"
                })
            }
        
        # Generar ID y preparar el ítem
        usuario_id = data['usuario_id']
        pago_id = str(uuid.uuid4())
        monto = datos_pago['monto']
        titulo = datos_pago['titulo']
        descripcion = datos_pago['descripcion']

        item = {
            'usuario_id': usuario_id,
            'pago_id': pago_id,
            'titulo': titulo,
            'descripcion': descripcion,
            'tipo': 'deuda',
            'monto': monto,
            'estado': 'pendiente',
            'fecha': datetime.utcnow().isoformat()
        }

        # Insertar en DynamoDB
        pagos_table.put_item(Item=item)

        # Respuesta de éxito
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': "Pago de deuda creado correctamente",
                'data': item
            })
        }

    except Exception as e:
        # Manejo de errores inesperados
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': "Error interno del servidor",
                'details': str(e)
            })
        }
