import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TABLA-SOPORTE')

def lambda_handler(event, context):
    data = json.loads(event['body'])
    usuario_id = data['usuario_id']
    
    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('usuario_id').eq(usuario_id)
    )
    
    return {
        'statusCode': 200,
        'body': response['Items']
    }
