import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.conf import settings


class PredictionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Extraer el schema del tenant actual
            tenant_schema = request.tenant.schema_name
            print(f"DEBUG: Tenant schema: {tenant_schema}")
            
            # Agregar tenant_schema al payload
            data = request.data.copy()
            data['tenant_schema'] = tenant_schema
            
            response = requests.post(
                f"{settings.PREDICTION_SERVICE_URL}/predecir",
                json=data,
                headers={
                    'Authorization': request.META.get('HTTP_AUTHORIZATION'),
                    'Content-Type': 'application/json'
                },
                timeout=30
            )
            return Response(response.json(), status=response.status_code)
        except requests.exceptions.RequestException as e:
            return Response(
                {'error': 'Prediction service unavailable', 'details': str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )