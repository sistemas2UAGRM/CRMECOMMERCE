# api/v1/ecommerce/services/catalog_service.py

"""
🛒 SERVICIO DE CATÁLOGO - E-COMMERCE

Servicio de negocio para gestión de catálogo:
- Gestión de categorías
- Listado de productos por categoría
- Búsquedas y filtros
- Estadísticas de productos

Principios aplicados:
- Single Responsibility: Solo gestión de catálogo
- Clean Architecture: Lógica de negocio separada
- Reusabilidad: Métodos compartidos entre views
"""

from django.db.models import Count, Q
from core.ecommerce.models import Categoria, Producto


class CatalogService:
    """
    Servicio para operaciones de catálogo de productos.
    
    Encapsula la lógica de negocio para:
    - Gestión de categorías
    - Consultas de productos
    - Filtros y búsquedas
    """
    
    @staticmethod
    def get_category_with_products(categoria_id):
        """
        Obtener categoría con sus productos.
        
        Args:
            categoria_id (int): ID de la categoría
            
        Returns:
            Categoria: Categoría con productos relacionados
            
        Raises:
            Categoria.DoesNotExist: Si la categoría no existe
        """
        return Categoria.objects.prefetch_related(
            'productos'
        ).get(id=categoria_id)
    
    @staticmethod
    def get_products_by_category(categoria_id, filters=None):
        """
        Obtener productos filtrados por categoría.
        
        Args:
            categoria_id (int): ID de la categoría
            filters (dict): Filtros adicionales
            
        Returns:
            QuerySet: Productos de la categoría
        """
        queryset = Producto.objects.filter(
            categoria_id=categoria_id,
            activo=True
        ).select_related('categoria')
        
        if filters:
            # Aplicar filtros adicionales
            if 'precio_min' in filters:
                queryset = queryset.filter(precio__gte=filters['precio_min'])
            if 'precio_max' in filters:
                queryset = queryset.filter(precio__lte=filters['precio_max'])
            if 'search' in filters:
                queryset = queryset.filter(
                    Q(nombre__icontains=filters['search']) |
                    Q(descripcion__icontains=filters['search'])
                )
        
        return queryset.order_by('nombre')
    
    @staticmethod
    def get_categories_with_stats():
        """
        Obtener categorías con estadísticas de productos.
        
        Returns:
            QuerySet: Categorías con conteo de productos
        """
        return Categoria.objects.annotate(
            total_productos=Count('productos'),
            productos_activos=Count(
                'productos',
                filter=Q(productos__activo=True)
            )
        ).order_by('nombre')
    
    @staticmethod
    def search_products(query, categoria_id=None):
        """
        Búsqueda de productos por texto.
        
        Args:
            query (str): Término de búsqueda
            categoria_id (int, optional): Filtrar por categoría
            
        Returns:
            QuerySet: Productos que coinciden con la búsqueda
        """
        queryset = Producto.objects.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query),
            activo=True
        ).select_related('categoria')
        
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        
        return queryset.order_by('nombre')
    
    @staticmethod
    def get_popular_products(limit=10):
        """
        Obtener productos más populares.
        
        Args:
            limit (int): Cantidad máxima de productos
            
        Returns:
            QuerySet: Productos ordenados por popularidad
        """
        # Por ahora ordenamos por fecha de creación
        # TODO: Implementar lógica de popularidad real basada en ventas
        return Producto.objects.filter(
            activo=True
        ).select_related('categoria').order_by('-fecha_creacion')[:limit]
