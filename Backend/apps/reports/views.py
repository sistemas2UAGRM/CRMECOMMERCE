import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http import HttpResponse
from django.conf import settings


class ReportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Extraer el schema del tenant actual
            tenant_schema = request.tenant.schema_name
            print(f"DEBUG: Tenant schema: {tenant_schema}")
            
            # Agregar tenant_schema al payload
            data = request.data.copy()
            data['tenant_schema'] = tenant_schema
            
            # Forward request to reports microservice
            print(f"DEBUG: Requesting report from {settings.REPORTS_SERVICE_URL}/generar-reporte-ia")
            response = requests.post(
                f"{settings.REPORTS_SERVICE_URL}/generar-reporte-ia",
                json=data
            )
            
            print(f"DEBUG: Microservice response status: {response.status_code}")
            print(f"DEBUG: Microservice headers: {response.headers}")
            print(f"DEBUG: Content type: {response.headers.get('Content-Type')}")
            print(f"DEBUG: Content length: {len(response.content)} bytes")
            print(f"DEBUG: First 50 bytes: {response.content[:50]}")

            # Create Django response with content from microservice
            django_response = HttpResponse(
                response.content,
                status=response.status_code,
                content_type=response.headers.get('Content-Type')
            )

            # Forward headers
            for header, value in response.headers.items():
                if header.lower() not in ['content-encoding', 'transfer-encoding', 'content-length', 'connection']:
                    django_response[header] = value
            
            print(f"DEBUG: Django response headers: {django_response.headers}")

            return django_response

        except requests.exceptions.RequestException as e:
            print(f"DEBUG: Error connecting to microservice: {e}")
            return Response(
                {'error': 'Reports service unavailable', 'details': str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )