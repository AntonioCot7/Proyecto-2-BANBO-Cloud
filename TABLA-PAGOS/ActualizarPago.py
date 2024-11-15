import boto3
import json
from datetime import datetime

# Inicializar DynamoDB
dynamodb = boto3.resource('dynamodb')
pagos_table = dynamodb.Table('TABLA-PAGOS')

def lambda_handler(event, context):
    try:
        # Parsear el cuerpo de la solicitud
        data = json.loads(event['body'])
        usuario_id = data['usuario_id']
        pago_id = data['pago_id']

        # Verificar si el pago existe en la base de datos
        response = pagos_table.get_item(Key={'usuario_id': usuario_id, 'pago_id': pago_id})
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Pago no encontrado'})
            }

        # Obtener el estado actual del pago
        pago = response['Item']
        estado_actual = pago.get('estado', 'pendiente')

        # Impedir la modificación del estado si ya está en "pagado"
        if estado_actual == 'pagado':
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'El pago ya ha sido completado y no se pueden modificar sus atributos',
                    'pago_id': pago_id,
                    'usuario_id': usuario_id,
                    'estado_actual': estado_actual
                })
            }

        # Preparar la actualización para todos los atributos excepto el estado
        titulo = data.get('titulo', pago.get('titulo'))
        descripcion = data.get('descripcion', pago.get('descripcion'))
        monto = data.get('monto', pago.get('monto'))
        fecha_modificacion = datetime.utcnow().isoformat()

        # Realizar la actualización
        pagos_table.update_item(
            Key={'usuario_id': usuario_id, 'pago_id': pago_id},
            UpdateExpression="SET titulo = :titulo, descripcion = :descripcion, monto = :monto, fecha_modificacion = :fecha",
            ExpressionAttributeValues={
                ':titulo': titulo,
                ':descripcion': descripcion,
                ':monto': monto,
                ':fecha': fecha_modificacion
            }
        )

        # Respuesta de éxito
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Pago {pago_id} actualizado con éxito',
                'usuario_id': usuario_id,
                'pago_id': pago_id,
                'titulo': titulo,
                'descripcion': descripcion,
                'monto': monto,
                'estado': estado_actual,  # Mantenemos el estado sin cambios
                'fecha_modificacion': fecha_modificacion
            })
        }

    except Exception as e:
        # Manejo de errores con respuesta detallada
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Error interno del servidor al actualizar el pago',
                'details': str(e)
            })
        }
