#apps/crm/crm_preventa/views.py
from rest_framework import viewsets, permissions
from django.contrib.contenttypes.models import ContentType
from .models import Potencial, Contacto, Oportunidad, Actividad
from .serializers import (
    PotencialSerializer,
    ContactoSerializer,
    OportunidadSerializer,
    ActividadSerializer
)

class PotencialViewSet(viewsets.ModelViewSet):
    """
    (ADMIN) CRUD completo para Potenciales (Leads).
    """
    queryset = Potencial.objects.all().order_by('-creado_en')
    serializer_class = PotencialSerializer
    permission_classes = [permissions.IsAdminUser] # Solo staff/admin
    filterset_fields = ['estado', 'fuente', 'propietario'] # Permitir filtrar por estado, etc.

class ContactoViewSet(viewsets.ModelViewSet):
    """
    (ADMIN) CRUD completo para Contactos.
    """
    queryset = Contacto.objects.all().order_by('-creado_en')
    serializer_class = ContactoSerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ['email', 'telefono']

class OportunidadViewSet(viewsets.ModelViewSet):
    """
    (ADMIN) CRUD completo para Oportunidades de Venta.
    """
    queryset = Oportunidad.objects.all().order_by('-creado_en')
    serializer_class = OportunidadSerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ['etapa', 'propietario', 'contacto']

class ActividadViewSet(viewsets.ModelViewSet):
    """
    (ADMIN) CRUD completo para Actividades (Seguimiento).
    Permite filtrar por el objeto relacionado (Potencial, Contacto, etc.).
    """
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        """
        Permite filtrar el historial de actividades por un objeto específico.
        Ej: GET /api/crm/actividades/?tipo_contenido=crm.potencial&id_objeto=123
        """
        queryset = super().get_queryset()
        
        # Filtros para el GenericForeignKey
        tipo_contenido_str = self.request.query_params.get('tipo_contenido', None)
        id_objeto = self.request.query_params.get('id_objeto', None)
        
        if tipo_contenido_str and id_objeto:
            try:
                app_label, model = tipo_contenido_str.split('.')
                content_type = ContentType.objects.get_for_model_name(
                    app_label=app_label, model=model
                )
                queryset = queryset.filter(
                    content_type=content_type, 
                    object_id=id_objeto
                )
            except ContentType.DoesNotExist:
                pass # Ignorar filtro si es inválido
        
        return queryset

    def get_serializer_context(self):
        """
        Pasa el 'request' al serializador para que sepa
        quién es el 'propietario' (empleado) que crea la actividad.
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context