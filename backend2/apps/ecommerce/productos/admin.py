from django.contrib import admin

from .models import Producto, Categoria, Almacen, ArticuloAlmacen, ImagenProducto

class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1

class ArticuloAlmacenInline(admin.TabularInline):
    model = ArticuloAlmacen
    extra = 1

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "precio", "moneda", "activo", "destacado", "creado_en")
    search_fields = ("codigo", "nombre")
    list_filter = ("activo", "destacado", "categorias")
    inlines = [ImagenProductoInline, ArticuloAlmacenInline]

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("nombre",)}

@admin.register(Almacen)
class AlmacenAdmin(admin.ModelAdmin):
    list_display = ("nombre", "codigo", "activo")
    search_fields = ("nombre", "codigo")
