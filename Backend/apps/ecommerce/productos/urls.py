# apps/ecommerce/productos/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet, CategoriaViewSet, AlmacenViewSet, StockMovimientoViewSet, cloudinary_sign

router = DefaultRouter()
router.register(r"productos", ProductoViewSet, basename="producto")
router.register(r"categorias", CategoriaViewSet, basename="categoria")
router.register(r"almacenes", AlmacenViewSet, basename="almacen")
router.register(r"movimientos-stock", StockMovimientoViewSet, basename="movimientostock")

urlpatterns = [
    path("", include(router.urls)),
    path("cloudinary/sign/", cloudinary_sign, name="cloudinary_sign"),
]
