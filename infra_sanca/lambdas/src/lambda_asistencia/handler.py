import json
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import json
import datetime

# Inicializa el cliente de DynamoDB
dynamodb = boto3.resource('dynamodb')

def mapear_respuesta_dynamo(response):
    """
    Mapea la respuesta de DynamoDB a un formato estructurado
    
    Args:
        response (dict): Respuesta cruda de DynamoDB
    
    Returns:
        dict: Respuesta mapeada con metadatos y items procesados
    """
    items = response.get('Items', [])
    
    # Procesar cada item si es necesario (convertir tipos de datos DynamoDB)
    items_procesados = []
    for item in items:
        item_procesado = {}
        for key, value in item.items():
            # Convertir tipos de datos DynamoDB a Python nativo
            if isinstance(value, dict):
                if 'S' in value:  # String
                    item_procesado[key] = value['S']
                elif 'N' in value:  # Number
                    try:
                        item_procesado[key] = float(value['N']) if '.' in value['N'] else int(value['N'])
                    except ValueError:
                        item_procesado[key] = value['N']
                elif 'BOOL' in value:  # Boolean
                    item_procesado[key] = value['BOOL']
                else:
                    item_procesado[key] = value
            else:
                item_procesado[key] = value
        items_procesados.append(item_procesado)
    
    # Construir respuesta estructurada
    resultado = {
        'items': items_procesados,
        'count': len(items),
        'scannedCount': response.get('ScannedCount', 0),
        'lastEvaluatedKey': response.get('LastEvaluatedKey'),
        'hasMore': 'LastEvaluatedKey' in response
    }
    print(f"resultados: {resultado}")
    
    return resultado


def listAsistenciasPorAlumno(event:dict)->dict:
    """
    Consulta la asistencia de un alumno en DynamoDB, opcionalmente filtrando por rango de fechas   
    
    """
    
    table = dynamodb.Table('asistencias')

    queryStringParameters = event.get("queryStringParameters")
    alumnoID = queryStringParameters.get("alumnoID","")
    fechaDesde = queryStringParameters.get("fechaDesde",None)
    fechaHasta = queryStringParameters.get("fechaHasta",None)
    
    try:
        # Construir la expresión de consulta basada en los parámetros
        if fechaDesde and fechaHasta:
            # Consulta con rango de fechas
            response = table.query(
                KeyConditionExpression=Key('alumnoID').eq(alumnoID) & 
                                     Key('fecha').between(fechaDesde, fechaHasta)
            )
        else:
            # Consulta solo por alumnoID
            response = table.query(
                KeyConditionExpression=Key('alumnoID').eq(alumnoID)
            )
        
        # Mapear la respuesta
        return mapear_respuesta_dynamo(response)
        
    except Exception as e:
        print(f"Error en la consulta: {str(e)}")
        return {
            'error': str(e),
            'items': [],
            'count': 0
        }

def lambda_handler(event, context):
    print(f"event: {event}")
    method = event.get("httpMethod")
    path = event.get("path")
    
    if method == "GET" and path == "/asistencia":
        body_response = listAsistenciasPorAlumno(event)
        return {
            "statusCode": 200,
            "body": json.dumps(body_response["items"])
        }
    
    elif method == "POST" and path == "/asistencia":
        return {
            "statusCode": 201,
            "body": json.dumps({"msg": "Crear asistencia"})
        }
    #elif method == "GET":
    #    return {
    #        "statusCode": 200,
    #        "body": json.dumps({"msg": "Obtener asistencia por ID"})
    #    }
    elif method == "PUT":
        return {
            "statusCode": 200,
            "body": json.dumps({"msg": "Actualizar asistencia"})
        }
    elif method == "DELETE":
        return {
            "statusCode": 200,
            "body": json.dumps({"msg": "Eliminar asistencia"})
        }
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Operación no soportada"})
        }
