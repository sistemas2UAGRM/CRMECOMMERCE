from rest_framework import serializers
from .models import Producto, Categoria, Almacen, ArticuloAlmacen, ImagenProducto

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre", "slug", "descripcion"]


class AlmacenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Almacen
        fields = ["id", "nombre", "codigo", "direccion", "telefono", "activo"]


class ArticuloAlmacenSerializer(serializers.ModelSerializer):
    almacen = AlmacenSerializer(read_only=True)
    almacen_id = serializers.PrimaryKeyRelatedField(queryset=Almacen.objects.all(), source="almacen", write_only=True)

    disponible = serializers.SerializerMethodField()

    class Meta:
        model = ArticuloAlmacen
        fields = [
            "id", "almacen", "almacen_id", "cantidad", "reservado",
            "lote", "fecha_vencimiento", "actualizado_en", "disponible"
        ]
        read_only_fields = ["actualizado_en", "disponible"]

    def get_disponible(self, obj):
        return obj.disponible()


class ImagenProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenProducto
        fields = ["id", "imagen", "texto_alt", "es_principal", "orden"]


class ProductoListSerializer(serializers.ModelSerializer):
    categorias = CategoriaSerializer(many=True, read_only=True)
    stock_total = serializers.IntegerField(read_only=True)

    class Meta:
        model = Producto
        fields = ["id", "codigo", "nombre", "slug", "precio", "moneda", "activo", "destacado", "categorias", "stock_total"]


class ProductoDetailSerializer(serializers.ModelSerializer):
    categorias = CategoriaSerializer(many=True, read_only=True)
    categoria_ids = serializers.PrimaryKeyRelatedField(queryset=Categoria.objects.all(), many=True, write_only=True, source="categorias")
    imagenes = ImagenProductoSerializer(many=True, required=False)
    almacenes = ArticuloAlmacenSerializer(source="articulos_almacen", many=True, read_only=True)

    class Meta:
        model = Producto
        fields = [
            "id", "codigo", "nombre", "slug", "descripcion", "precio", "costo", "moneda",
            "peso", "dimensiones", "activo", "destacado", "categorias", "categoria_ids",
            "imagenes", "almacenes", "creado_en", "actualizado_en", "meta_titulo", "meta_descripcion"
        ]
        read_only_fields = ["creado_en", "actualizado_en", "slug"]

    def create(self, validated_data):
        categorias = validated_data.pop("categorias", [])
        imagenes_datos = self.initial_data.get("imagenes", None)
        producto = Producto.objects.create(**validated_data)
        if categorias:
            producto.categorias.set(categorias)
        if imagenes_datos:
            for img in imagenes_datos:
                ImagenProducto.objects.create(producto=producto, **img)
        return producto

    def update(self, instance, validated_data):
        categorias = validated_data.pop("categorias", None)
        imagenes_datos = self.initial_data.get("imagenes", None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        if categorias is not None:
            instance.categorias.set(categorias)
        if imagenes_datos is not None:
            instance.imagenes.all().delete()
            for img in imagenes_datos:
                ImagenProducto.objects.create(producto=instance, **img)
        return instance
