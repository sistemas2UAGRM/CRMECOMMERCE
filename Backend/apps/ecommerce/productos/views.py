# apps/ecommerce/productos/views.py
import time
import hashlib
from django.conf import settings
from rest_framework import viewsets, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response 
from django.db.models import Sum
from rest_framework.permissions import BasePermission, IsAuthenticated
from .models import Producto, Categoria, Almacen, ArticuloAlmacen, StockMovimiento

from .serializers import (
    ProductoListSerializer, ProductoDetailSerializer,
    CategoriaSerializer, AlmacenSerializer, ArticuloAlmacenSerializer, StockMovimientoSerializer
)

class EsAdminOSoloLectura(BasePermission):
    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return bool(request.user and request.user.is_staff)


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all().prefetch_related("categorias", "imagenes").order_by('-creado_en')
    permission_classes = [EsAdminOSoloLectura]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre", "codigo", "descripcion", "categorias__nombre"]
    ordering_fields = ["precio", "creado_en", "nombre"]

    def get_serializer_class(self):
        if self.action in ("list",):
            return ProductoListSerializer
        return ProductoDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.annotate(stock_total=Sum("articulos_almacen__cantidad") - Sum("articulos_almacen__reservado"))


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [EsAdminOSoloLectura]


class AlmacenViewSet(viewsets.ModelViewSet):
    queryset = Almacen.objects.all()
    serializer_class = AlmacenSerializer
    permission_classes = [EsAdminOSoloLectura]

    @action(detail=True, methods=["get"])
    def articulos(self, request, pk=None):
        almacen = self.get_object()
        items = ArticuloAlmacen.objects.filter(almacen=almacen).select_related("producto")
        serializer = ArticuloAlmacenSerializer(items, many=True)
        return Response(serializer.data)


class StockMovimientoViewSet(viewsets.ModelViewSet):
    queryset = StockMovimiento.objects.all().select_related("producto", "almacen", "usuario")
    serializer_class = StockMovimientoSerializer
    permission_classes = [EsAdminOSoloLectura]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["producto__nombre", "producto__codigo", "almacen__nombre", "referencia"]
    ordering_fields = ["creado_en", "producto__nombre"]


# --- Cloudinary signing endpoint (signed uploads) ---
@api_view(["POST"]) # Cambiado a POST para poder enviar parámetros en el body
@permission_classes([IsAuthenticated])
def cloudinary_sign(request):
    """
    Genera una firma para que el cliente pueda subir un archivo directamente a Cloudinary.
    """
    timestamp = int(time.time())
    
    # --- CAMBIOS AQUÍ ---
    # Parámetros que quieres firmar. El frontend debe enviarlos EXACTAMENTE IGUAL.
    # El folder es importante para que se suba donde quieres.
    folder = request.data.get('folder', 'boutique/productos') # Recibir folder desde el cliente
    
    # Construir el string a firmar en orden alfabético de las claves
    to_sign_params = {
        'folder': folder,
        'timestamp': timestamp
    }

    # Ordenar por clave y concatenar
    to_sign_string = "&".join([f"{k}={v}" for k, v in sorted(to_sign_params.items())])
    
    to_sign_string += settings.CLOUDINARY_STORAGE['API_SECRET']
    
    signature = hashlib.sha1(to_sign_string.encode("utf-8")).hexdigest()
    
    return Response({
        "signature": signature,
        "timestamp": timestamp,
        "api_key": settings.CLOUDINARY_STORAGE['API_KEY'],
        "cloud_name": settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
        "folder": folder 
    })