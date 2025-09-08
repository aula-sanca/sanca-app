import json
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
import json
from datetime import datetime

# Inicializa el cliente de DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('asistencias')

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

def createRegistro(event:dict)->dict:
    """
    crear Registro    
    """
    bodyRq = json.loads(event.get("body"))
    
    # Genera las marcas de tiempo en formato ISO8601
    now_iso = datetime.now().isoformat()

    bodyRq["createdAt"] = now_iso

    # Construye el objeto a insertar en DynamoDB
    item = bodyRq

    # Elimina las claves con valores None para evitar errores
    item = {k: v for k, v in item.items() if v is not None}
    
    # Realiza la operación PutItem en DynamoDB
    table.put_item(Item=item)
    
    # Retorna el item insertado como respuesta
    return item

def updateRegistro(event:dict)->dict:
    """
    Actualiza datos de tabla
    """
    bodyRq = json.loads(event.get("body"))
    
    # Genera las marcas de tiempo en formato ISO8601
    now_iso = datetime.now().isoformat()
    bodyRs = {}

    try:
        # Extraer la clave primaria (id) y los datos de entrada
        alumnoID = event.get('pathParameters', {}).get('alumnoID')
        fecha = bodyRq.get("fecha",None)
        # Replicar la lógica del VTL para la fecha
        final_fecha = fecha if fecha and fecha.strip() else datetime.now().isoformat()[:10]

        print(f"alumnoID: {alumnoID}")    

        if not alumnoID or not bodyRq:
            raise ValueError("alumnoID y los datos de entrada son obligatorios.")

        # Construir la expresión de actualización dinámicamente
        update_expression_parts = []
        expression_attribute_values = {}

        bodyRq["updatedAt"] = now_iso
        
        for key, value in bodyRq.items():
            # Excluir claves que no se van a actualizar (como la clave primaria)
            if key != 'alumnoID' and value is not None:
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
                'alumnoID': alumnoID,
                'fecha': final_fecha
            },
            UpdateExpression="SET #estado = :estado, #updatedAt = :updatedAt",
            ExpressionAttributeNames={
                "#estado": "estado",
                "#updatedAt": "updatedAt"
            },
            ExpressionAttributeValues={
                ':estado': bodyRq.get('estado'),
                ':updatedAt': datetime.now().isoformat()
            },
            ReturnValues="ALL_NEW"
        )
        
        # Retornar el ítem actualizado
        print(f"response_atributtes: {response.get('Attributes')}")
        return response.get('Attributes')

    except ClientError as e:
        # Manejar el error de condición, que ocurre si el ítem no existe
        
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            print(f"Error: El registro con alumnoID '{alumnoID}' no existe y no se puede actualizar.")
            bodyRs = {
                    "error": "Registro no encontrado",
                    "message": "No se encontró el registro para el 'id' especificado."
                    }
            return bodyRs
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
    
def listRegistros(event:dict)->dict:
    
    try:
        # Realiza la operación Scan
        response = table.scan()
        bodyRs  = mapear_respuesta_dynamo(response)
        bodyRs = {
            "asistencias": bodyRs["items"]
        }
        
        # Retorna los items encontrados
        return bodyRs
        
    except ClientError as e:
        print(f"Error al escanear la tabla: {e.response['Error']['Message']}")
        return {
                "error": "Error interno",
                "message": "No se pudo completar el escaneo de la tabla."
            }
        
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return {
                "error": "Error interno",
                "message": "Error inesperado."
            }
        
def listRegistrosPorId(event:dict)->dict:
    
    try:
        
        alumnoID = event.get('pathParameters', {}).get('alumnoID',None)
        escuelaID = event.get('pathParameters', {}).get('escuelaID',None)
        gradoID = event.get('pathParameters', {}).get('gradoID',None)

        print(f"alumnoID: {alumnoID}")
        print(f"escuelaID: {escuelaID}")
        print(f"gradoID: {gradoID}")
        
        if event.get("queryStringParameters",None):
            fecha_desde = event.get("queryStringParameters",{}).get('fecha_desde',None)
            fecha_hasta = event.get("queryStringParameters",{}).get('fecha_hasta',None)
        else:
            fecha_desde = None
            fecha_hasta = None
        print(f"fecha_desde: {fecha_desde}")
        print(f"fecha_hasta: {fecha_hasta}")

        if not alumnoID and not escuelaID and not gradoID:
            return {"statusCode": 400, "body": "Debe indicar alumnoID, escuelaID or gradoID"}

        if alumnoID:
            # Caso 1: Si se reciben fecha_desde y fecha_hasta diferentes -> usar between
            if fecha_desde and fecha_hasta and fecha_desde != fecha_hasta:
                response = table.query(
                    KeyConditionExpression=Key("alumnoID").eq(alumnoID) & Key("fecha").between(fecha_desde, fecha_hasta)
                )

            # Caso 2: Si solo viene fecha_desde o ambas son iguales -> buscar ese día
            elif fecha_desde:
                fecha_actual = datetime.now().strftime('%Y-%m-%d')
                response = table.query(
                    KeyConditionExpression=Key("alumnoID").eq(alumnoID) & Key("fecha").between(fecha_desde, fecha_actual)
                )

            # Caso 3: Solo alumnoID (sin rango de fechas)
            else:
                response = table.query(
                    KeyConditionExpression=Key("alumnoID").eq(alumnoID)
                )

        elif escuelaID:
            if fecha_desde and fecha_hasta and fecha_desde != fecha_hasta:
                response = table.query(
                    IndexName="escuelaID-fecha-index",
                    KeyConditionExpression=Key("escuelaID").eq(escuelaID) & Key("fecha").between(fecha_desde, fecha_hasta)
                )
            elif fecha_desde:
                fecha_actual = datetime.now().strftime('%Y-%m-%d')
                response = table.query(
                    IndexName="escuelaID-fecha-index",
                    KeyConditionExpression=Key("escuelaID").eq(escuelaID) & Key("fecha").between(fecha_desde, fecha_actual)
                )
            else:
                response = table.query(
                    IndexName="escuelaID-fecha-index",
                    KeyConditionExpression=Key("escuelaID").eq(escuelaID)
                )

        elif gradoID:
            if fecha_desde and fecha_hasta and fecha_desde != fecha_hasta:
                response = table.query(
                    IndexName="gradoID-fecha-index",
                    KeyConditionExpression=Key("gradoID").eq(gradoID) & Key("fecha").between(fecha_desde, fecha_hasta)
                )
            elif fecha_desde:
                fecha_actual = datetime.now().strftime('%Y-%m-%d')
                response = table.query(
                    IndexName="gradoID-fecha-index",
                    KeyConditionExpression=Key("gradoID").eq(gradoID) & Key("fecha").between(fecha_desde, fecha_actual)
                )
            else:
                response = table.query(
                    IndexName="gradoID-fecha-index",
                    KeyConditionExpression=Key("gradoID").eq(gradoID)
                )

        # Devuelve la lista de elementos encontrados
        print(f"response: {response.get('Items', [])}")
        return response.get('Items', [])

    except ClientError as e:
        print(f"Error al consultar DynamoDB: {e.response['Error']['Message']}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Error interno",
                "message": "Ocurrió un error al procesar la consulta."
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
        
def deleteRegistro(event:dict)->dict:
    
    try:
        alumnoID = event.get('pathParameters', {}).get('alumnoID')
        if event.get("queryStringParameters",None):
            fecha= event.get("queryStringParameters",{}).get('fecha',None)            
        else:
            fecha = None            

        if not alumnoID:
            raise ValueError("El argumento 'alumnoID' es obligatorio.")
        
        # Lógica para determinar la fecha, igual que en el VTL
        final_fecha = fecha if fecha and fecha.strip() else datetime.now().isoformat()[:10]

        # Realiza la operación DeleteItem
        response = table.delete_item(
            Key={
                'alumnoID': alumnoID,
                'fecha': final_fecha
            },
            ConditionExpression="attribute_exists(alumnoID) AND attribute_exists(fecha)",
            ReturnValues="ALL_OLD"
        )
        
        # Devuelve el ítem que fue eliminado para confirmar la operación
        deleted_item = response.get('Attributes')
        if deleted_item:
            return {
                    "message": "Registro eliminado exitosamente.",
                    "deletedItem": deleted_item
                }            
        else:
            return {"message": "El registro ya no existe o no fue encontrado."}
            

    except ClientError as e:
        # Maneja el error si el ítem no existe (Condición de verificación fallida)
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            print(f"Error: El registro con id '{id}' no existe y no se puede eliminar.")
            return {
                    "error": "Registro no encontrado",
                    "message": "No se encontró el registro para el 'id' especificado."
                }
            
        else:
            print(f"Error al eliminar de DynamoDB: {e.response['Error']['Message']}")
            return {
                    "error": "Error interno",
                    "message": "Ocurrió un error al intentar eliminar el registro."
                }
            
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return {
                "error": "Error inesperado",
                "message": "Ocurrió un error inesperado al procesar la solicitud."
            }
        
def lambda_handler(event, context):
    print(f"event: {event}")
    method = event.get("httpMethod")
    path = event.get("path")
    
    if method == "GET" and path == "/asistencias":
        body_response = listRegistros(event)
        return {
            "statusCode": 200,
            "body": json.dumps(body_response)
        }
    
    elif method == "POST" and path == "/asistencias":
        body_response = createRegistro(event)
        return {
            "statusCode": 200,
            "body": json.dumps(body_response)
        }
    
    elif method == "GET":
        body_response = listRegistrosPorId(event)
        return {
            "statusCode": 200,
            "body": json.dumps(body_response)
        }
    
    elif method == "PUT":
        body_response = updateRegistro(event)
        return {
            "statusCode": 200,
            "body": json.dumps(body_response)
        }
    
    elif method == "DELETE":
        body_response = deleteRegistro(event)
        return {
            "statusCode": 200,
            "body": json.dumps(body_response)
        }
    
    else:  
        body_response = {
            "error_code": "0001",
            "error_msg": "Recurso invalido"
        }      
        return {
            "statusCode": 400,
            "body": json.dumps(body_response)
        }
