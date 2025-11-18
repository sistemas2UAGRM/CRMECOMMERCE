# apps/crm/clientes/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# --- Router para Vistas de Administración ---
# Generará /admin/segmentos/ y /admin/clientes/
router_admin = DefaultRouter()
router_admin.register(r'segmentos', views.AdminSegmentoViewSet, basename='admin-segmento')
router_admin.register(r'clientes', views.AdminClienteViewSet, basename='admin-cliente')

# --- Lista principal de URLs de la app ---
urlpatterns = [
    # --- Vista para el Cliente ---
    # GET /api/clientes/mi-perfil/
    path('mi-perfil/', views.MiPerfilClienteView.as_view(), name='mi-perfil-cliente'),

    # --- Vistas de Administración ---
    # /api/clientes/admin/
    path('admin/', include(router_admin.urls)),
]