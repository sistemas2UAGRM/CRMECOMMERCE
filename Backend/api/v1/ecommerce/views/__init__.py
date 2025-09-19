# api/v1/ecommerce/views/__init__.py

"""
📚 VIEWS MODULARES PARA E-COMMERCE

Este módulo organiza las views en archivos especializados:

- catalog_views.py: Catálogo y categorías
- product_views.py: Gestión de productos
- cart_views.py: Carrito de compras
- inventory_views.py: Control de inventario

Beneficios:
- Separación clara de responsabilidades
- Archivos más pequeños y enfocados
- Fácil mantenimiento y escalabilidad
- Reutilización de servicios de negocio
"""

# Importar todas las views para mantener compatibilidad
from .catalog_views import CategoriaViewSet
from .product_views import ProductoViewSet
from .cart_views import CarritoViewSet
from .inventory_views import InventoryStatsView

# Mantener compatibilidad con imports existentes
__all__ = [
    'CategoriaViewSet',
    'ProductoViewSet', 
    'CarritoViewSet',
    'InventoryStatsView'
]
