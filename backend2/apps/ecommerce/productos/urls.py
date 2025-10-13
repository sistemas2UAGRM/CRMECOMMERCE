from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet, CategoriaViewSet, AlmacenViewSet

router = DefaultRouter()
router.register(r"productos", ProductoViewSet, basename="producto")
router.register(r"categorias", CategoriaViewSet, basename="categoria")
router.register(r"almacenes", AlmacenViewSet, basename="almacen")

urlpatterns = [
    path("", include(router.urls)),
]
