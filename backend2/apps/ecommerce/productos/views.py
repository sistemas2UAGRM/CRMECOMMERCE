from django.shortcuts import render

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from rest_framework.permissions import BasePermission

from .models import Producto, Categoria, Almacen, ArticuloAlmacen
from .serializers import (
    ProductoListSerializer, ProductoDetailSerializer,
    CategoriaSerializer, AlmacenSerializer, ArticuloAlmacenSerializer
)

class EsAdminOSoloLectura(BasePermission):
    """
    Permisos: métodos seguros (GET/HEAD/OPTIONS) abiertos,
    métodos de escritura solo para usuarios staff.
    """
    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return bool(request.user and request.user.is_staff)


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all().prefetch_related("categorias", "imagenes")
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
        # Annotate stock_total usando la relación articulos_almacen
        return qs.annotate(stock_total=Sum("articulos_almacen__cantidad"))


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [EsAdminOSoloLectura]
    #lookup_field = "slug"

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
