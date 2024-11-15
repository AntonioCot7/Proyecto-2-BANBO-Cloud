import boto3
import json

# Conexión a DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TABLA-SOPORTE')

def lambda_handler(event, context):
    try:
        # Realizar un escaneo completo en DynamoDB para obtener todas las solicitudes
        response = table.scan()
        
        # Devolver la lista de todas las solicitudes
        return {
            'statusCode': 200,
            'body': json.dumps(response['Items'])  # Convertir a JSON
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error interno del servidor: {str(e)}")
        }
