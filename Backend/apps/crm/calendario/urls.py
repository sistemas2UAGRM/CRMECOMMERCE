# apps/crm/calendario/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Esta vista es solo para admin/staff
router = DefaultRouter()
router.register(r'eventos', views.EventoCalendarioViewSet, basename='evento-calendario')

urlpatterns = [
    # Esto generará:
    # GET, POST /api/calendario/eventos/
    # GET, PUT /api/calendario/eventos/{id}/
    path('', include(router.urls)),
]