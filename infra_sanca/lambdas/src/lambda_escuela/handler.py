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

def createEscuela(event:dict)->dict:
    """
    crear la escuela    
    """
    bodyRq = json.loads(event.get("body"))
    
    table = dynamodb.Table('escuelas')

    # Genera las marcas de tiempo en formato ISO8601
    now_iso = datetime.datetime.now().isoformat()

    # Construye el objeto a insertar en DynamoDB
    item = {
        'cct': bodyRq.get('cct'),
        'nivel_escolar': bodyRq.get('nivel_escolar'),
        'entidad': bodyRq.get('entidad'),
        'municipio': bodyRq.get('municipio'),
        'localidad': bodyRq.get('localidad'),
        'direccion': bodyRq.get('direccion'),
        'nombre': bodyRq.get('nombre'),
        'sostenimiento': bodyRq.get('sostenimiento'),        
        'createdAt': now_iso,
        'updatedAt': now_iso
    }

    # Elimina las claves con valores None para evitar errores
    item = {k: v for k, v in item.items() if v is not None}
    
    # Realiza la operación PutItem en DynamoDB
    table.put_item(Item=item)
    
    # Retorna el item insertado como respuesta
    return item

def updateEscuela(event:dict)->dict:
    """
    Actualiza datos de la escuela    
    """
    bodyRq = json.loads(event.get("body"))
    
    table = dynamodb.Table('escuelas')
    # Genera las marcas de tiempo en formato ISO8601
    now_iso = datetime.datetime.now().isoformat()

    try:
        # Extraer la clave primaria (cct) y los datos de entrada
        cct = event.get('pathParameters', {}).get('id')
        print(f"cct: {cct}")    

        if not cct or not bodyRq:
            raise ValueError("cct y los datos de entrada son obligatorios.")

        # Construir la expresión de actualización dinámicamente
        update_expression_parts = []
        expression_attribute_values = {}

        bodyRq["updatedAt"] = now_iso
        
        for key, value in bodyRq.items():
            # Excluir claves que no se van a actualizar (como la clave primaria)
            if key != 'cct' and value is not None:
                update_expression_parts.append(f"{key} = :{key}")
                expression_attribute_values[f":{key}"] = value

        # Si no hay datos para actualizar, no hace nada
        if not update_expression_parts:
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "No hay atributos para actualizar."})
            }

        update_expression = "SET " + ", ".join(update_expression_parts)
        print(f"update_expression: {update_expression}")
        print(f"expression_attribute_values: {expression_attribute_values}")

        # Realizar la operación de actualización
        response = table.update_item(
            Key={
                'cct': cct
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ConditionExpression="attribute_exists(cct)",
            ReturnValues="ALL_NEW"
        )
        
        # Retornar el ítem actualizado
        print(f"response_atributtes: {response.get('Attributes')}")
        return response.get('Attributes')

    except ClientError as e:
        # Manejar el error de condición, que ocurre si el ítem no existe
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            print(f"Error: El registro con cct '{cct}' no existe y no se puede actualizar.")
            return {
                "statusCode": 404,
                "body": json.dumps({
                    "error": "Registro no encontrado",
                    "message": "No se encontró el registro para el 'cct' especificado."
                })
            }
        else:
            print(f"Error al actualizar DynamoDB: {e.response['Error']['Message']}")
            raise e
    
    except Exception as e:
        print(f"Error inesperado: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Error interno",
                "message": str(e)
            })
        }
    
def listEscuelas(event:dict)->dict:
    
    table = dynamodb.Table('escuelas')
    
    try:
        # Realiza la operación Scan
        response = table.scan()
        bodyRs  = mapear_respuesta_dynamo(response)
        bodyRs = {
            "escuelas": bodyRs["items"]
        }
        
        # Retorna los items encontrados
        return bodyRs
        
    except ClientError as e:
        print(f"Error al escanear la tabla: {e.response['Error']['Message']}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Error interno",
                "message": "No se pudo completar el escaneo de la tabla."
            })
        }
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Error interno",
                "message": "Error inesperado."
            })
        }

def getEscuela(event:dict)->dict:
   
    table = dynamodb.Table('escuelas')
    try:
        # Extrae la clave primaria 'cct' del evento
        cct = event.get('pathParameters', {}).get('id')

        if not cct:
            raise ValueError("El argumento 'cct' es obligatorio.")

        # Realiza la operación GetItem para obtener un solo registro
        response = table.get_item(
            Key={
                'cct': cct
            }
        )
        
        # Retorna el item si se encuentra, de lo contrario retorna None
        return response["Item"]
        
    except ClientError as e:
        print(f"Error al obtener el registro de DynamoDB: {e.response['Error']['Message']}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Error interno",
                "message": e.response['Error']['Message']
            })
        }
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Error inesperado",
                "message": "Ocurrió un error inesperado al procesar la solicitud."
            })
        } 

def deleteEscuela(event:dict)->dict:

    table = dynamodb.Table('escuelas')
    try:
        cct = event.get('pathParameters', {}).get('id')

        if not cct:
            raise ValueError("El argumento 'cct' es obligatorio.")
        
        # Realiza la operación DeleteItem
        response = table.delete_item(
            Key={
                'cct': cct
            },
            ConditionExpression="attribute_exists(cct)",
            ReturnValues="ALL_OLD"
        )
        
        # Devuelve el ítem que fue eliminado para confirmar la operación
        deleted_item = response.get('Attributes')
        if deleted_item:
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Registro eliminado exitosamente.",
                    "deletedItem": deleted_item
                })
            }
        else:
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "El registro ya no existe o no fue encontrado."})
            }

    except ClientError as e:
        # Maneja el error si el ítem no existe (Condición de verificación fallida)
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            print(f"Error: El registro con cct '{cct}' no existe y no se puede eliminar.")
            return {
                "statusCode": 404,
                "body": json.dumps({
                    "error": "Registro no encontrado",
                    "message": "No se encontró el registro para el 'cct' especificado."
                })
            }
        else:
            print(f"Error al eliminar de DynamoDB: {e.response['Error']['Message']}")
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "error": "Error interno",
                    "message": "Ocurrió un error al intentar eliminar el registro."
                })
            }
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Error inesperado",
                "message": "Ocurrió un error inesperado al procesar la solicitud."
            })
        }

def lambda_handler(event, context):
    print(f"event: {event}")
    method = event.get("httpMethod")
    path = event.get("path")
    
    if method == "GET" and path == "/escuelas":
        body_response = listEscuelas(event)
        return {
            "statusCode": 200,
            "body": json.dumps(body_response)
        }
    
    elif method == "POST" and path == "/escuelas":
        body_response = createEscuela(event)
        return {
            "statusCode": 200,
            "body": json.dumps(body_response)
        }
    elif method == "GET":
        body_response = getEscuela(event)
        return {
            "statusCode": 200,
            "body": json.dumps(body_response)
        }
    elif method == "PUT":
        body_response = updateEscuela(event)
        return {
            "statusCode": 200,
            "body": json.dumps(body_response)
        }
    elif method == "DELETE":
        body_response = deleteEscuela(event)
        return {
            "statusCode": body_response["statusCode"],
            "body": body_response["body"]
        }
    else:  
        body_response = {
            "error_code": "0001",
            "error_msg": "Recurso invalido"
        }      
        return {
            "statusCode": 400,
            "body": json.dumps(body_response["items"])
        }
