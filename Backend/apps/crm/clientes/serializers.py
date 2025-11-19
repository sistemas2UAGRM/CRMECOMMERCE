# apps/crm/clientes/serializers.py
from rest_framework import serializers
from .models import Cliente, Segmento
from apps.crm.crm_preventa.serializers import UsuarioSimpleSerializer
from apps.users.models import User as CustomUser

class SegmentoSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Segmento (CRUD para Admin).
    """
    class Meta:
        model = Segmento
        fields = ('id', 'nombre', 'descripcion')

class ClienteSerializer(serializers.ModelSerializer):
    """
    Serializador para el "Perfil 360" (Modelo Cliente).
    Se usa tanto para el cliente (lectura) como para el admin (lectura/escritura).
    """
    # Para LEER, mostramos el objeto de usuario (email, nombre)
    usuario = UsuarioSimpleSerializer(read_only=True)
    
    # Para LEER, mostramos los objetos de segmento
    segmentos = SegmentoSerializer(many=True, read_only=True)
    # Para ESCRIBIR, aceptamos una lista de IDs de segmento
    segmentos_ids = serializers.PrimaryKeyRelatedField(
        queryset=Segmento.objects.all(),
        source='segmentos',
        many=True,
        write_only=True,
        required=False # No es requerido en cada actualización
    )

    # Para ESCRIBIR, aceptamos el ID del usuario
    usuario_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source='usuario',
        write_only=True,
        required=True
    )

    # Campo para mostrar el display del estado
    estado_display = serializers.SerializerMethodField()

    def get_estado_display(self, obj):
        return obj.get_estado_display()

    class Meta:
        model = Cliente
        fields = (
            'id',
            'usuario',
            'usuario_id',      # Para escribir
            'estado',           # Para escribir (ej: "VIP")
            'estado_display',   # Para leer (ej: "VIP")
            'segmentos',        # Para leer
            'segmentos_ids',    # Para escribir
            # Campos de solo lectura (calculados por signals)
            'total_gastado',
            'total_pedidos',
            'fecha_ultima_compra',
            'creado_en',
            'actualizado_en'
        )
        # Los campos calculados y el usuario son siempre de solo lectura
        read_only_fields = (
            'id', 
            'usuario', 
            'total_gastado', 
            'total_pedidos', 
            'fecha_ultima_compra',
            'creado_en', 
            'actualizado_en'
        )