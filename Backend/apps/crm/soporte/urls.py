# apps/crm/soporte/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# --- Router para Vistas de Administración ---
router_admin = DefaultRouter()
router_admin.register(
    r'tickets', 
    views.AdminTicketViewSet, 
    basename='admin-ticket'
)

# --- Router para Vistas de Cliente ---
router_cliente = DefaultRouter()
router_cliente.register(
    r'tickets', 
    views.ClienteTicketViewSet, 
    basename='cliente-ticket'
)

# --- Lista principal de URLs de la app ---
urlpatterns = [
    # --- Vistas de Administración ---
    # GET, PATCH /api/soporte/admin/tickets/
    path('admin/', include(router_admin.urls)),

    # --- Vista de Acción (Responder) ---
    # POST /api/soporte/tickets/{ticket_pk}/responder/
    path(
        'tickets/<int:ticket_pk>/responder/', 
        views.MensajeCreateView.as_view(), 
        name='ticket-responder'
    ),
    
    # --- Vistas de Cliente ---
    # GET, POST /api/soporte/tickets/
    # (Debe ir al final para que /admin/ y /responder/ se detecten primero)
    path('', include(router_cliente.urls)),
]