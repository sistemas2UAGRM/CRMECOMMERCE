# api/v1/ecommerce/urls.py

"""
📚 URLS MODULARES PARA E-COMMERCE

Estructura de URLs para el módulo de e-commerce refactorizado:

1. CATÁLOGO: /productos/, /categorias/
2. CARRITOS: /carritos/, /carritos/mi-carrito/
3. INVENTARIO: /inventario/stats/, /inventario/stock-bajo/
4. RELACIONES: /categorias/{id}/productos/

Casos de uso implementados: CU-E01 al CU-E13 (Sprint 1)
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Importar views modulares
from .views import (
    CategoriaViewSet, ProductoViewSet, CarritoViewSet
)
from .views.inventory_views import InventoryStatsView, LowStockProductsView

# Router para ViewSets principales
router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'productos', ProductoViewSet, basename='producto') 
router.register(r'carritos', CarritoViewSet, basename='carrito')

urlpatterns = [
    # ViewSet URLs principales
    path('', include(router.urls)),
    
    # URLs específicas de inventario
    path('inventario/stats/', InventoryStatsView.as_view(), name='inventario-stats'),
    path('inventario/stock-bajo/', LowStockProductsView.as_view(), name='inventario-stock-bajo'),
]

"""
📝 MICROCONCEPTO: URLs generadas para E-commerce

Router genera automáticamente:

GESTIÓN DE CATEGORÍAS (CU-E01):
- GET /api/v1/ecommerce/categorias/ -> CategoriaViewSet.list()
- POST /api/v1/ecommerce/categorias/ -> CategoriaViewSet.create()
- GET /api/v1/ecommerce/categorias/{id}/ -> CategoriaViewSet.retrieve()
- PUT /api/v1/ecommerce/categorias/{id}/ -> CategoriaViewSet.update()
- DELETE /api/v1/ecommerce/categorias/{id}/ -> CategoriaViewSet.destroy()

PRODUCTOS POR CATEGORÍA (CU-E12):
- GET /api/v1/ecommerce/categorias/{id}/productos/ -> CategoriaViewSet.productos()

GESTIÓN DE PRODUCTOS (CU-E02, CU-E03, CU-E04):
- GET /api/v1/ecommerce/productos/ -> ProductoViewSet.list() (Catálogo)
- POST /api/v1/ecommerce/productos/ -> ProductoViewSet.create()
- GET /api/v1/ecommerce/productos/{id}/ -> ProductoViewSet.retrieve()
- PUT /api/v1/ecommerce/productos/{id}/ -> ProductoViewSet.update()
- DELETE /api/v1/ecommerce/productos/{id}/ -> ProductoViewSet.destroy()

ACTUALIZAR STOCK (CU-E05):
- PUT /api/v1/ecommerce/productos/{id}/stock/ -> ProductoViewSet.stock()

FILTROS Y ESTADÍSTICAS (CU-E11, CU-E13):
- GET /api/v1/ecommerce/productos/por-estado/ -> ProductoViewSet.por_estado()
- GET /api/v1/ecommerce/productos/stats/ -> ProductoViewSet.stats()
- GET /api/v1/ecommerce/productos/por-estado/resumen/ -> ResumenEstadosView

GESTIÓN DE CARRITOS (CU-E06, CU-E07, CU-E08, CU-E09, CU-E10):
- GET /api/v1/ecommerce/carritos/ -> CarritoViewSet.list()
- POST /api/v1/ecommerce/carritos/ -> CarritoViewSet.create()
- GET /api/v1/ecommerce/carritos/{id}/ -> CarritoViewSet.retrieve()
- GET /api/v1/ecommerce/carritos/mi-carrito/ -> CarritoViewSet.mi_carrito()
- POST /api/v1/ecommerce/carritos/{id}/productos/ -> CarritoViewSet.productos()

Ejemplos de uso:

CATÁLOGO:
- GET /api/v1/ecommerce/productos/ -> Listar todos los productos
- GET /api/v1/ecommerce/productos/?search=laptop -> Buscar productos
- GET /api/v1/ecommerce/productos/?ordering=precio_venta -> Ordenar por precio

FILTROS:
- GET /api/v1/ecommerce/productos/por-estado/?estado=disponible
- GET /api/v1/ecommerce/productos/por-estado/?estado=agotado
- GET /api/v1/ecommerce/productos/por-estado/?estado=no_disponible

CARRITOS:
- GET /api/v1/ecommerce/carritos/mi-carrito/ -> Ver mi carrito actual
- POST /api/v1/ecommerce/carritos/1/productos/ -> Agregar producto al carrito
  Body: {"producto_id": 5, "cantidad": 2}

CATEGORÍAS:
- GET /api/v1/ecommerce/categorias/1/productos/ -> Productos de una categoría
- GET /api/v1/ecommerce/productos/stats/ -> Estadísticas (solo admin/supervisor)
"""
