# api/v1/common/serializers.py

"""
📚 MICROCONCEPTOS - SERIALIZERS PARA AUDITORÍA Y LOGGING

Los sistemas de auditoría requieren serializers especiales porque:
1. Generalmente son de solo lectura
2. Incluyen información de usuarios y timestamps
3. Necesitan filtrado y paginación eficiente
4. Pueden incluir datos sensibles que requieren permisos especiales
"""

from rest_framework import serializers
from core.common.models import Bitacora
from core.users.models import User


class UserBasicInfoSerializer(serializers.ModelSerializer):
    """
    📝 MICROCONCEPTO: Serializer anidado para información básica
    
    Cuando incluimos información de usuario en bitácora,
    no queremos exponer todos los datos del usuario,
    solo información básica y segura.
    """
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class BitacoraListSerializer(serializers.ModelSerializer):
    """
    📝 MICROCONCEPTO: Serializers optimizados para listados
    
    Para listados grandes como bitácora, es importante:
    - Incluir solo campos necesarios
    - Usar select_related/prefetch_related en las vistas
    - Evitar SerializerMethodField costosos
    """
    
    # Serializer anidado para información del usuario
    usuario = UserBasicInfoSerializer(read_only=True)
    
    class Meta:
        model = Bitacora
        fields = ['id', 'accion', 'fecha', 'ip', 'usuario']
        read_only_fields = ['id', 'accion', 'fecha', 'ip', 'usuario']


class BitacoraDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado para una entrada específica de bitácora
    """
    
    usuario = UserBasicInfoSerializer(read_only=True)
    tiempo_transcurrido = serializers.SerializerMethodField()
    
    class Meta:
        model = Bitacora
        fields = ['id', 'accion', 'fecha', 'ip', 'usuario', 'tiempo_transcurrido']
        read_only_fields = ['id', 'accion', 'fecha', 'ip', 'usuario']
        
    def get_tiempo_transcurrido(self, obj):
        """
        📝 MICROCONCEPTO: Campos calculados con información útil
        
        Calculamos tiempo transcurrido desde la acción para
        dar contexto temporal al usuario.
        """
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - obj.fecha
        
        if diff.days > 0:
            return f"Hace {diff.days} días"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"Hace {hours} horas"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"Hace {minutes} minutos"
        else:
            return "Hace menos de un minuto"


class BitacoraCreateSerializer(serializers.ModelSerializer):
    """
    📝 MICROCONCEPTO: Serializer para creación automática
    
    Este serializer se usa internamente para registrar acciones.
    Incluye validaciones específicas para datos de auditoría.
    """
    
    usuario_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Bitacora
        fields = ['accion', 'ip', 'usuario_id']
        
    def validate_accion(self, value):
        """Validar que la acción no esté vacía y tenga formato apropiado"""
        if not value or not value.strip():
            raise serializers.ValidationError("La acción no puede estar vacía.")
            
        # Limitar longitud para evitar spam
        if len(value) > 255:
            raise serializers.ValidationError("La acción es demasiado larga (máximo 255 caracteres).")
            
        return value.strip()
        
    def validate_ip(self, value):
        """Validar formato de IP"""
        import ipaddress
        try:
            ipaddress.ip_address(value)
        except ValueError:
            raise serializers.ValidationError("Formato de IP inválido.")
        return value
        
    def validate_usuario_id(self, value):
        """Validar que el usuario existe"""
        if value:
            try:
                User.objects.get(id=value)
            except User.DoesNotExist:
                raise serializers.ValidationError("Usuario no encontrado.")
        return value
        
    def create(self, validated_data):
        """
        📝 MICROCONCEPTO: Manejo de relaciones en create()
        
        Convertimos usuario_id a instancia de usuario antes de crear.
        """
        usuario_id = validated_data.pop('usuario_id', None)
        if usuario_id:
            try:
                usuario = User.objects.get(id=usuario_id)
                validated_data['usuario'] = usuario
            except User.DoesNotExist:
                # Si el usuario no existe, creamos la entrada sin usuario
                pass
                
        return super().create(validated_data)


class BitacoraStatsSerializer(serializers.Serializer):
    """
    📝 MICROCONCEPTO: Serializer para estadísticas
    
    Para datos agregados y estadísticas, usamos Serializer base
    ya que no corresponden a un modelo específico.
    """
    
    total_acciones = serializers.IntegerField()
    acciones_hoy = serializers.IntegerField()
    acciones_ultima_semana = serializers.IntegerField()
    usuarios_activos_hoy = serializers.IntegerField()
    acciones_por_tipo = serializers.DictField()
    ips_mas_frecuentes = serializers.ListField()
    
    def to_representation(self, instance):
        """
        📝 MICROCONCEPTO: Formateo personalizado de estadísticas
        
        Podemos formatear los datos para que sean más útiles
        para el frontend.
        """
        data = super().to_representation(instance)
        
        # Formatear acciones por tipo para gráficos
        if 'acciones_por_tipo' in data:
            data['acciones_por_tipo_chart'] = [
                {'tipo': k, 'cantidad': v}
                for k, v in data['acciones_por_tipo'].items()
            ]
            
        return data


class BitacoraFilterSerializer(serializers.Serializer):
    """
    📝 MICROCONCEPTO: Serializer para filtros de búsqueda
    
    Útil para validar parámetros de filtrado antes de aplicarlos
    a las consultas de base de datos.
    """
    
    fecha_inicio = serializers.DateTimeField(required=False)
    fecha_fin = serializers.DateTimeField(required=False)
    usuario_id = serializers.IntegerField(required=False)
    accion_contiene = serializers.CharField(max_length=100, required=False)
    ip = serializers.IPAddressField(required=False)
    
    def validate(self, data):
        """
        📝 MICROCONCEPTO: Validación de rangos de fechas
        
        Validamos que el rango de fechas sea lógico.
        """
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        if fecha_inicio and fecha_fin:
            if fecha_inicio > fecha_fin:
                raise serializers.ValidationError({
                    'fecha_inicio': 'La fecha de inicio no puede ser posterior a la fecha de fin.'
                })
                
        # Validar que no se solicite un rango muy amplio
        if fecha_inicio and fecha_fin:
            diff = fecha_fin - fecha_inicio
            if diff.days > 365:
                raise serializers.ValidationError({
                    'fecha_fin': 'El rango de fechas no puede ser mayor a un año.'
                })
                
        return data
        
    def validate_usuario_id(self, value):
        """Validar que el usuario existe"""
        if value:
            if not User.objects.filter(id=value).exists():
                raise serializers.ValidationError("Usuario no encontrado.")
        return value
