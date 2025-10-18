# apps/ecommerce/productos/serializers.py
from rest_framework import serializers
from .models import Producto, Categoria, Almacen, ArticuloAlmacen, ImagenProducto, StockMovimiento
from django.db import transaction

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nombre", "slug", "descripcion"]

class AlmacenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Almacen
        fields = ["id", "nombre", "codigo", "direccion", "telefono", "activo"]

class ImagenProductoSerializer(serializers.ModelSerializer):
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = ImagenProducto
        fields = ["id", "imagen_url", "texto_alt", "es_principal", "orden"]
        read_only_fields = ["id", "imagen_url"]

    def get_imagen_url(self, obj):
        return obj.imagen or None

class ProductoListSerializer(serializers.ModelSerializer):
    categorias = CategoriaSerializer(many=True, read_only=True)
    stock_total = serializers.IntegerField(read_only=True)
    imagen_principal_url = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = ["id", "codigo", "nombre", "slug", "precio", "moneda", "activo", 
                  "destacado", "categorias", "stock_total", "imagen_principal_url"
        ]

    def get_imagen_principal_url(self, obj):
        return obj.imagen_principal_url

class ArticuloAlmacenSerializer(serializers.ModelSerializer):
    almacen = AlmacenSerializer(read_only=True)
    almacen_id = serializers.PrimaryKeyRelatedField(queryset=Almacen.objects.all(), source="almacen", write_only=True)
    disponible = serializers.SerializerMethodField()
    producto = ProductoListSerializer(read_only=True)

    class Meta:
        model = ArticuloAlmacen
        fields = [
            "id", "almacen", "almacen_id", "cantidad", "reservado",
            "lote", "fecha_vencimiento", "actualizado_en", "disponible",
            "producto"
        ]
        read_only_fields = ["actualizado_en", "disponible"]

    def get_disponible(self, obj):
        return obj.disponible()


class ProductoDetailSerializer(serializers.ModelSerializer):
    categorias = CategoriaSerializer(many=True, read_only=True)
    categoria_ids = serializers.PrimaryKeyRelatedField(queryset=Categoria.objects.all(), many=True, write_only=True, source="categorias")
    almacenes = ArticuloAlmacenSerializer(source="articulos_almacen", many=True, read_only=True)

    # 'imagenes' ahora recibirá una lista de objetos con la URL de Cloudinary.
    imagenes = ImagenProductoSerializer(many=True, read_only=True) # Solo para leer
    imagenes_payload = serializers.ListField( # Campo para escribir
        child=serializers.JSONField(),
        write_only=True,
        required=False
    )

    almacenes_stock = serializers.ListField(
        child=serializers.JSONField(), write_only=True, required=False
    )

    class Meta:
        model = Producto
        fields = [
            "id", "codigo", "nombre", "slug", "descripcion", "precio", "costo", "moneda",
            "peso", "dimensiones", "activo", "destacado", "categorias", "categoria_ids",
            "imagenes", "imagenes_payload", # <-- Añadir imagenes_payload
            "almacenes_stock", "almacenes", "creado_en", "actualizado_en", "meta_titulo", "meta_descripcion"
        ]
        read_only_fields = ["creado_en", "actualizado_en", "slug", "imagenes"]

    def _create_or_update_imagenes(self, producto, imagenes_payload):
        # Borramos las imágenes existentes para simplificar la lógica de actualización
        producto.imagenes.all().delete()
        for img_data in imagenes_payload:
            ImagenProducto.objects.create(
                producto=producto,
                imagen=img_data.get("url"), 
                texto_alt=img_data.get("texto_alt", ""),
                es_principal=img_data.get("es_principal", False),
                orden=img_data.get("orden", 0)
            )

    def create(self, validated_data):
        categorias = validated_data.pop("categorias", [])
        imagenes_payload = validated_data.pop("imagenes_payload", [])
        almacenes_stock = validated_data.pop("almacenes_stock", [])

        with transaction.atomic():
            producto = Producto.objects.create(**validated_data)
            if categorias:
                producto.categorias.set(categorias)
            if imagenes_payload:
                self._create_or_update_imagenes(producto, imagenes_payload)

            # Si vienen stocks iniciales, crear ArticuloAlmacen + StockMovimiento (entrada)
            if almacenes_stock and isinstance(almacenes_stock, list):
                for item in almacenes_stock:
                    try:
                        almacen_id = int(item.get("almacen"))
                        cantidad = int(item.get("cantidad") or 0)
                    except Exception:
                        continue
                    if cantidad == 0:
                        continue
                    almacen = Almacen.objects.filter(id=almacen_id).first()
                    if not almacen:
                        continue
                    art, created = ArticuloAlmacen.objects.get_or_create(producto=producto, almacen=almacen, defaults={"cantidad": 0})
                    art.cantidad = (art.cantidad or 0) + cantidad
                    art.save()
                    StockMovimiento.objects.create(
                        producto=producto,
                        almacen=almacen,
                        cantidad=abs(cantidad),
                        tipo="entrada",
                        referencia="Stock inicial al crear producto",
                        comentario="Creación de producto con stock inicial",
                        usuario=None
                    )

        return producto

    def _update_stock(self, producto, almacenes_stock):
        # Esta lógica puede ser tan simple o compleja como necesites.
        # Por ejemplo, aquí simplemente actualizamos las cantidades.
        for item in almacenes_stock:
            try:
                almacen_id = int(item.get("almacen"))
                cantidad = int(item.get("cantidad") or 0)
                almacen = Almacen.objects.get(id=almacen_id)
                
                articulo, created = ArticuloAlmacen.objects.get_or_create(
                    producto=producto, 
                    almacen=almacen
                )
                
                # Aquí podrías generar un StockMovimiento si la cantidad cambia
                if articulo.cantidad != cantidad:
                    articulo.cantidad = cantidad
                    articulo.save()

            except (Almacen.DoesNotExist, ValueError, TypeError):
                continue

    def update(self, instance, validated_data):
        categorias = validated_data.pop("categorias", None)
        imagenes_payload = validated_data.pop("imagenes_payload", None)
        almacenes_stock = validated_data.pop("almacenes_stock", None)

        instance = super().update(instance, validated_data)
        if categorias is not None:
            instance.categorias.set(categorias)
        if imagenes_payload is not None:
            self._create_or_update_imagenes(instance, imagenes_payload)
        if almacenes_stock is not None:
            self._update_stock(instance, almacenes_stock) 

        return instance


class StockMovimientoSerializer(serializers.ModelSerializer):
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all())
    almacen = serializers.PrimaryKeyRelatedField(queryset=Almacen.objects.all())

    class Meta:
        model = StockMovimiento
        fields = ["id", "producto", "almacen", "cantidad", "tipo", "referencia", "comentario", "usuario", "creado_en"]
        read_only_fields = ["creado_en", "usuario"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user and not validated_data.get("usuario"):
            validated_data["usuario"] = request.user
        movimiento = super().create(validated_data)

        from django.db import transaction
        with transaction.atomic():
            art, created = ArticuloAlmacen.objects.select_for_update().get_or_create(producto=movimiento.producto, almacen=movimiento.almacen, defaults={"cantidad": 0})
            art.cantidad = (art.cantidad or 0) + movimiento.cantidad
            if art.cantidad < 0:
                raise serializers.ValidationError("Cantidad resultante en almacén no puede ser negativa.")
            art.save()
        return movimiento
