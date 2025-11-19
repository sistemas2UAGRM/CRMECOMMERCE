# backend/apps/ia_services/views.py
import requests
import json
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db import connection # <--- CORRECCIÓN 1: Importación completa

# Define tus URLs aquí o impórtalas de settings.py
URL_SERVICIO_REPORTES = "http://127.0.0.1:8001/generar-reporte-ia"
URL_SERVICIO_PREDICCION = "http://127.0.0.1:8002/predecir"

@csrf_exempt
@require_POST
def llamar_servicio_prediccion(request):
    """
    Vista "puente" que llama al microservicio de predicción.
    Recibe: {"dias_a_predecir": 7}
    Devuelve: {"predicciones": [...]}
    """
    try:
        # 1. Obtenemos los datos que envió el frontend
        data = json.loads(request.body)
        dias = data.get('dias_a_predecir')

        if not dias:
            return JsonResponse({'error': 'Faltan dias_a_predecir'}, status=400)

        # 2. Preparamos la petición para FastAPI
        payload = {'dias_a_predecir': dias}

        # 3. ¡LA LLAMADA! Usamos requests.post()
        # Le pasamos el JSON (payload) y un timeout
        response = requests.post(URL_SERVICIO_PREDICCION, json=payload, timeout=10)

        # 4. Verificamos si el microservicio dio un error
        response.raise_for_status() # Lanza un error si la respuesta es 4xx o 5xx

        # 5. Devolvemos la respuesta (que es un JSON) al frontend
        return JsonResponse(response.json())

    except requests.exceptions.ConnectionError:
        # El microservicio está apagado
        return JsonResponse({'error': 'El servicio de predicción no está disponible.'}, status=503)
    except requests.exceptions.HTTPError as e:
        # El microservicio dio un error (ej. 400, 500)
        try:
            error_detail = e.response.json()
        except:
            error_detail = e.response.text
        return JsonResponse({'error': f'Error del microservicio: {error_detail}'}, status=e.response.status_code)
    except Exception as e:
        # Otro error (ej. JSON inválido, timeout)
        return JsonResponse({'error': f'Ocurrió un error inesperado: {str(e)}'}, status=500)


@csrf_exempt
@require_POST
def llamar_servicio_reporte(request):
    """
    Vista "puente" que llama al microservicio de reportes
    y devuelve el archivo Excel, PDF O el JSON de datos.
    """
    try:
        # 1. LEER DATOS (ESTO DEBE IR PRIMERO)
        # Primero leemos el body para tener 'prompt' y 'formato' disponibles
        data = json.loads(request.body)
        prompt = data.get('prompt')
        formato = data.get('formato', 'json') # Default a json si no viene

        if not prompt:
            return JsonResponse({'error': 'Falta el prompt'}, status=400)

        # 2. Obtener el schema actual (Multi-tenant)
        # Esto es lo que permite que la IA sepa de qué cliente sacar los datos
        schema_name = connection.schema_name 

        # 3. Preparar el payload completo
        payload = {
            'prompt': prompt,
            'format': formato,
            'schema_name': schema_name  # <--- ¡CRUCIAL!
        }

        # 4. Llamar al Microservicio
        # Usamos stream=True para manejar archivos binarios (Excel/PDF) sin saturar memoria
        response = requests.post(URL_SERVICIO_REPORTES, json=payload, stream=True, timeout=60)
        
        # 5. Verificar errores del microservicio (4xx o 5xx)
        response.raise_for_status()

        # 6. Revisamos QUÉ TIPO de respuesta recibimos y la devolvemos al frontend
        
        # Si es un archivo (Excel o PDF), tendrá este header
        if 'Content-Disposition' in response.headers:
            return StreamingHttpResponse(
                response.iter_content(chunk_size=8192),
                content_type=response.headers['Content-Type'],
                headers={
                    'Content-Disposition': response.headers['Content-Disposition']
                }
            )
        else:
            # Si es JSON (texto plano o datos), lo devolvemos normal
            return JsonResponse(response.json())
        
    except requests.exceptions.HTTPError as e:
        # Error si FastAPI devuelve 4xx o 5xx (ej. prompt no entendido)
        try:
            error_json = e.response.json()
        except:
            error_json = e.response.text
        return JsonResponse({'error': f'Error del microservicio: {error_json}'}, status=e.response.status_code)
    
    except requests.exceptions.ConnectionError:
        return JsonResponse({'error': 'El servicio de reportes no está disponible.'}, status=503)
    
    except Exception as e:
        # Cualquier otro error (ej. JSON malformado en el request inicial)
        return JsonResponse({'error': f'Ocurrió un error inesperado en Django: {str(e)}'}, status=500)