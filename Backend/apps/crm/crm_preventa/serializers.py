#apps/crm/crm_preventa/serializers.py
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import Potencial, Contacto, Oportunidad, Actividad
from apps.users.models import User as CustomUser

# --- Serializadores de Ayuda (para anidar) ---
class UsuarioSimpleSerializer(serializers.ModelSerializer):
    """
    Un serializador simple para mostrar info básica del
    propietario (empleado/admin) de un potencial o actividad.
    """
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name')


class ContactoSimpleSerializer(serializers.ModelSerializer):
    """
    Serializador simple para mostrar info básica de un Contacto
    dentro de una Oportunidad.
    """
    class Meta:
        model = Contacto
        fields = ('id', 'nombre', 'apellido', 'email')


# --- Serializadores Principales del CRM ---
class PotencialSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Potencial (Lead).
    """
    # Para LEER, mostramos el objeto simple del propietario
    propietario = UsuarioSimpleSerializer(read_only=True)
    # Para ESCRIBIR, aceptamos el ID del propietario
    propietario_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(is_staff=True), # Solo empleados pueden ser propietarios
        source='propietario',
        write_only=True,
        required=False, # El propietario se puede asignar después
        allow_null=True
    )
    
    # Campos de solo lectura para mostrar el texto ("Nuevo", "Instagram")
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    fuente_display = serializers.CharField(source='get_fuente_display', read_only=True)

    class Meta:
        model = Potencial
        fields = (
            'id', 'nombre_completo', 'email', 'telefono', 'empresa', 
            'fuente', 'fuente_display',  # 'fuente' es para escribir (ej: "INSTAGRAM")
            'estado', 'estado_display',  # 'estado' es para escribir (ej: "NUEVO")
            'propietario', 'propietario_id', 
            'creado_en', 'actualizado_en'
        )
        read_only_fields = ('id', 'creado_en', 'actualizado_en')


class ContactoSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Contacto.
    """
    # El "puente" al usuario de e-commerce
    usuario_ecommerce = UsuarioSimpleSerializer(read_only=True)
    class Meta:
        model = Contacto
        fields = (
            'id', 'nombre', 'apellido', 'email', 'telefono', 'empresa',
            'potencial_origen', # Se puede asignar al crear
            'usuario_ecommerce', # Solo lectura, se asigna por lógica interna
            'creado_en', 'actualizado_en'
        )
        read_only_fields = ('id', 'usuario_ecommerce', 'creado_en', 'actualizado_en')


class OportunidadSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Oportunidad.
    """
    propietario = UsuarioSimpleSerializer(read_only=True)
    propietario_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(is_staff=True),
        source='propietario', 
        write_only=True, 
        required=False
    )
    
    contacto = ContactoSimpleSerializer(read_only=True)
    contacto_id = serializers.PrimaryKeyRelatedField(
        queryset=Contacto.objects.all(),
        source='contacto', 
        write_only=True
    )
    
    etapa_display = serializers.CharField(source='get_etapa_display', read_only=True)
    
    # El "puente" al pedido de e-commerce
    pedido_ecommerce = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Oportunidad
        fields = (
            'id', 'nombre', 'monto_estimado', 'fecha_cierre_estimada',
            'etapa', 'etapa_display',
            'contacto', 'contacto_id',
            'propietario', 'propietario_id', 
            'pedido_ecommerce',
            'creado_en', 'actualizado_en'
        )
        read_only_fields = ('id', 'pedido_ecommerce', 'creado_en', 'actualizado_en')


class ActividadSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Actividad (Seguimiento).
    Maneja el GenericForeignKey.
    """
    propietario = UsuarioSimpleSerializer(read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    # --- Campos para ESCRITURA del GenericForeignKey ---
    
    # Aceptará "crm.potencial", "crm.contacto", "crm.oportunidad"
    tipo_contenido = serializers.CharField(
        write_only=True, 
        help_text="Modelo al que se vincula (ej: 'crm.potencial')"
    )
    # Aceptará el ID del objeto
    id_objeto = serializers.IntegerField(
        write_only=True, 
        help_text="ID del Potencial, Contacto u Oportunidad"
    )

    # --- Campo para LECTURA del GenericForeignKey ---
    relacionado_con = serializers.SerializerMethodField()

    class Meta:
        model = Actividad
        fields = (
            'id', 'propietario', 'tipo', 'tipo_display', 'notas', 'fecha_actividad',
            'tipo_contenido', 'id_objeto', # Solo escritura
            'relacionado_con'              # Solo lectura
        )
        read_only_fields = ('id', 'propietario', 'fecha_actividad')

    def get_relacionado_con(self, obj):
        """
        Devuelve una representación simple del objeto vinculado
        (ej: "Potencial: Juan Pérez")
        """
        if obj.content_object:
            return f"{obj.content_type.name.capitalize()}: {str(obj.content_object)}"
        return None

    def create(self, validated_data):
        tipo_contenido_str = validated_data.pop('tipo_contenido')
        id_objeto = validated_data.pop('id_objeto')
        
        # Encontrar el ContentType (el "tipo" de modelo)
        try:
            app_label, model = tipo_contenido_str.split('.')
            content_type = ContentType.objects.get(app_label=app_label, model=model)
        except (ContentType.DoesNotExist, ValueError):
            raise serializers.ValidationError("Tipo de contenido inválido. Use 'app.modelo' (ej: 'crm.potencial')")
        
        # Asignar el propietario (el empleado logueado) desde el contexto
        propietario = self.context['request'].user
        
        actividad = Actividad.objects.create(
            content_type=content_type,
            object_id=id_objeto,
            propietario=propietario,
            **validated_data
        )
        return actividad