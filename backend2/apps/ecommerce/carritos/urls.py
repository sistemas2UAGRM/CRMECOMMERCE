# /apps/ecommerce/carritos/urls.py
from django.urls import path
from .views import CarritoViewSet

# No usamos router porque es un recurso singleton (uno por usuario)
carrito_list = CarritoViewSet.as_view({'get': 'list'})
carrito_agregar = CarritoViewSet.as_view({'post': 'agregar_item'})
carrito_eliminar = CarritoViewSet.as_view({'delete': 'eliminar_item'})
carrito_crear_pedido = CarritoViewSet.as_view({'post': 'crear_pedido'})

urlpatterns = [
    path('', carrito_list, name='carrito-detail'),
    path('agregar_item/', carrito_agregar, name='carrito-agregar-item'),
    path('items/<int:pk>/eliminar/', carrito_eliminar, name='carrito-eliminar-item'),
    path('crear_pedido/', carrito_crear_pedido, name='carrito-crear-pedido'),
]