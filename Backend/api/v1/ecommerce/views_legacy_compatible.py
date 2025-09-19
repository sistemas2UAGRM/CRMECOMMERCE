# api/v1/ecommerce/views_legacy_compatible.py

"""
🔄 CAPA DE COMPATIBILIDAD LEGACY - E-COMMERCE

Esta capa mantiene la compatibilidad con el código existente
mientras se migra gradualmente a la nueva arquitectura modular.

⚠️ DEPRECADO: Este archivo será eliminado una vez completada la migración.

Redirecciona llamadas del ViewSet monolítico original a las nuevas views modulares.
"""

from rest_framework import viewsets
from rest_framework.decorators import action

# Importar nuevas views modulares
from .views import CategoriaViewSet, ProductoViewSet, CarritoViewSet


class EcommerceCompatibilityViewSet(viewsets.ViewSet):
    """
    ViewSet de compatibilidad que mantiene la interfaz original
    mientras redirige a las nuevas views modulares.
    
    🚨 TEMPORAL: Para migración gradual
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Instanciar nuevas views
        self._categoria_view = CategoriaViewSet()
        self._producto_view = ProductoViewSet()
        self._carrito_view = CarritoViewSet()
    
    def _setup_view(self, view, request, *args, **kwargs):
        """Configurar view con request y argumentos"""
        view.request = request
        view.format_kwarg = getattr(request, 'format_kwarg', None)
        view.args = args
        view.kwargs = kwargs
        return view
    
    # ============================================================
    # DELEGACIÓN A CATEGORIAS
    # ============================================================
    
    @action(detail=False, url_path='categorias', url_name='categorias-list')
    def list_categorias(self, request):
        """Delegar listado de categorías"""
        view = self._setup_view(self._categoria_view, request)
        return view.list(request)
    
    @action(detail=True, url_path='categorias/(?P<categoria_pk>[^/.]+)', url_name='categorias-detail')
    def retrieve_categoria(self, request, categoria_pk=None):
        """Delegar detalle de categoría"""
        view = self._setup_view(self._categoria_view, request, pk=categoria_pk)
        return view.retrieve(request, pk=categoria_pk)
    
    @action(detail=True, url_path='categorias/(?P<categoria_pk>[^/.]+)/productos', url_name='categoria-productos')
    def categoria_productos(self, request, categoria_pk=None):
        """Delegar productos de categoría"""
        view = self._setup_view(self._categoria_view, request, pk=categoria_pk)
        return view.productos(request, pk=categoria_pk)
    
    # ============================================================
    # DELEGACIÓN A PRODUCTOS
    # ============================================================
    
    @action(detail=False, url_path='productos', url_name='productos-list')
    def list_productos(self, request):
        """Delegar listado de productos"""
        view = self._setup_view(self._producto_view, request)
        return view.list(request)
    
    @action(detail=True, url_path='productos/(?P<producto_pk>[^/.]+)', url_name='productos-detail')
    def retrieve_producto(self, request, producto_pk=None):
        """Delegar detalle de producto"""
        view = self._setup_view(self._producto_view, request, pk=producto_pk)
        return view.retrieve(request, pk=producto_pk)
    
    @action(detail=False, url_path='productos/buscar', url_name='productos-buscar')
    def buscar_productos(self, request):
        """Delegar búsqueda de productos"""
        view = self._setup_view(self._producto_view, request)
        return view.buscar(request)
    
    @action(detail=False, url_path='productos/populares', url_name='productos-populares')
    def productos_populares(self, request):
        """Delegar productos populares"""
        view = self._setup_view(self._producto_view, request)
        return view.populares(request)
    
    @action(detail=False, url_path='productos/stats', url_name='productos-stats')
    def productos_stats(self, request):
        """Delegar estadísticas de productos"""
        view = self._setup_view(self._producto_view, request)
        return view.stats(request)
    
    # ============================================================
    # DELEGACIÓN A CARRITO
    # ============================================================
    
    @action(detail=False, url_path='carrito', url_name='carrito-mi-carrito')
    def mi_carrito(self, request):
        """Delegar mi carrito"""
        view = self._setup_view(self._carrito_view, request)
        return view.mi_carrito(request)
    
    @action(detail=False, url_path='carrito/agregar', url_name='carrito-agregar', methods=['post'])
    def agregar_al_carrito(self, request):
        """Delegar agregar al carrito"""
        view = self._setup_view(self._carrito_view, request)
        return view.agregar_producto(request)
    
    @action(detail=False, url_path='carrito/actualizar', url_name='carrito-actualizar', methods=['patch'])
    def actualizar_carrito(self, request):
        """Delegar actualizar carrito"""
        view = self._setup_view(self._carrito_view, request)
        return view.actualizar_cantidad(request)
    
    @action(detail=False, url_path='carrito/eliminar', url_name='carrito-eliminar', methods=['delete'])
    def eliminar_del_carrito(self, request):
        """Delegar eliminar del carrito"""
        view = self._setup_view(self._carrito_view, request)
        return view.eliminar_producto(request)
    
    @action(detail=False, url_path='carrito/vaciar', url_name='carrito-vaciar', methods=['delete'])
    def vaciar_carrito(self, request):
        """Delegar vaciar carrito"""
        view = self._setup_view(self._carrito_view, request)
        return view.vaciar(request)


# Alias para mantener compatibilidad con imports existentes
CategoriaLegacyViewSet = CategoriaViewSet  # Ya está modularizada
ProductoLegacyViewSet = ProductoViewSet    # Ya está modularizada  
CarritoLegacyViewSet = CarritoViewSet      # Ya está modularizada
