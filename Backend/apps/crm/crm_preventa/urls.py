# apps/crm/crm_preventa/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Todas estas vistas son solo para admin/staff
router = DefaultRouter()
router.register(r'potenciales', views.PotencialViewSet, basename='potencial')
router.register(r'contactos', views.ContactoViewSet, basename='contacto')
router.register(r'oportunidades', views.OportunidadViewSet, basename='oportunidad')
router.register(r'actividades', views.ActividadViewSet, basename='actividad')

urlpatterns = [
    # Esto generará todas las URLs del CRM
    # Ej: GET, POST /api/crm/potenciales/
    # Ej: GET, PUT /api/crm/potenciales/{id}/
    # Ej: GET /api/crm/actividades/?tipo_contenido=crm.potencial&id_objeto=1
    path('', include(router.urls)),
]