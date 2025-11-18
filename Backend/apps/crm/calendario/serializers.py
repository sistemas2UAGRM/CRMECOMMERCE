#apps/crm/calendario/serializers.py
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import EventoCalendario
from apps.users.models import User as CustomUser
from apps.crm.crm_preventa.serializers import UsuarioSimpleSerializer

class EventoCalendarioSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo EventoCalendario.
    """
    propietario = UsuarioSimpleSerializer(read_only=True)
    
    # Para LEER
    invitados = UsuarioSimpleSerializer(many=True, read_only=True)
    # Para ESCRIBIR
    invitados_ids = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(is_staff=True), # Solo invitar empleados
        source='invitados', 
        many=True, 
        write_only=True, 
        required=False
    )

    # --- Campos para el GenericForeignKey (igual que en Actividad) ---
    tipo_contenido = serializers.CharField(
        write_only=True, required=False, allow_null=True,
        help_text="Modelo al que se vincula (ej: 'crm.contacto')"
    )
    id_objeto = serializers.IntegerField(
        write_only=True, required=False, allow_null=True,
        help_text="ID del Contacto u Oportunidad"
    )
    relacionado_con = serializers.SerializerMethodField()
    # --- Fin GenericForeignKey ---

    class Meta:
        model = EventoCalendario
        fields = (
            'id', 'titulo', 'descripcion', 'fecha_inicio', 'fecha_fin',
            'propietario', 
            'invitados', 'invitados_ids',
            'tipo_contenido', 'id_objeto', 'relacionado_con'
        )
        read_only_fields = ('id', 'propietario')

    def get_relacionado_con(self, obj):
        """Devuelve una representación simple del objeto vinculado."""
        if obj.content_object:
            return f"{obj.content_type.name.capitalize()}: {str(obj.content_object)}"
        return None

    def create(self, validated_data):
        # El propietario es el usuario que hace la petición
        validated_data['propietario'] = self.context['request'].user
        
        tipo_contenido_str = validated_data.pop('tipo_contenido', None)
        id_objeto = validated_data.pop('id_objeto', None)
        
        # Si se proporcionan, los asignamos
        if tipo_contenido_str and id_objeto:
            try:
                app_label, model = tipo_contenido_str.split('.')
                content_type = ContentType.objects.get(app_label=app_label, model=model)
                validated_data['content_type'] = content_type
                validated_data['object_id'] = id_objeto
            except (ContentType.DoesNotExist, ValueError):
                raise serializers.ValidationError("Tipo de contenido inválido.")
        
        # El .pop() de 'invitados_ids' lo maneja 'super().create()'
        return super().create(validated_data)