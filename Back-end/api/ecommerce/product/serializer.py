from rest_framework import serializers
from api.ecommerce.category.models import Categoria
from api.ecommerce.category.serializer import CategoriaSerializer
from .models import Producto

class ProductoSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Categoria.objects.all())
    
    class Meta:
        model = Producto
        fields = [
            'id',
            'name',
            'description',
            'price',
            'stock_min',
            'stock_actual',
            'category',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        producto = Producto(**validated_data)
        producto.save()
        return producto

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['category'] = CategoriaSerializer(instance.category).data
        return representation
