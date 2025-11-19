# backend/apps/ecommerce/pedidos/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PedidoViewSet, DetallePedidoViewSet


router = DefaultRouter()
router.register(r'', PedidoViewSet, basename='pedido')
router.register(r'detalles', DetallePedidoViewSet, basename='detallepedido')

urlpatterns = [

    path('', include(router.urls)),
]
