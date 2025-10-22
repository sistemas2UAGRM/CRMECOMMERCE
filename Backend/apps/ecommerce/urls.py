# NUEVO ARCHIVO: /apps/ecommerce/urls.py
from django.urls import path, include

urlpatterns = [
    path('', include('apps.ecommerce.productos.urls')), # Incluye productos, categorias, etc.
    path('pedidos/', include('apps.ecommerce.pedidos.urls')),
    path('carrito/', include('apps.ecommerce.carritos.urls')),
    path('pagos/', include('apps.ecommerce.pagos.urls')), 
]