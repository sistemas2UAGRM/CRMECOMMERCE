# apps/crm/urls.py
from django.urls import path, include

urlpatterns = [
    path('crm_preventa/', include('apps.crm.crm_preventa.urls')),
    path('calendario/', include('apps.crm.calendario.urls')),
    path('clientes/', include('apps.crm.clientes.urls')),
    path('soporte/', include('apps.crm.soporte.urls')),
]