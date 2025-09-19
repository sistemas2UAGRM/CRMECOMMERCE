from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class HealthCheckView(APIView):
    """
    Endpoint simple para verificar que la API funciona
    """
    
    @swagger_auto_schema(
        operation_description="Verificar estado de la API",
        responses={
            200: openapi.Response(
                description='API funcionando correctamente',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'timestamp': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            )
        },
        tags=['Sistema']
    )
    def get(self, request):
        from django.utils import timezone
        return Response({
            'status': 'ok',
            'message': 'API CRM+Ecommerce funcionando correctamente',
            'timestamp': timezone.now().isoformat(),
        })
