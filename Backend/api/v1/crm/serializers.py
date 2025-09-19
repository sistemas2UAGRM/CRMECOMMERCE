# api/v1/crm/serializers.py

"""
📚 MICROCONCEPTOS - SERIALIZERS PARA RELACIONES

En Django REST Framework, manejar relaciones entre modelos es crucial:

1. PrimaryKeyRelatedField: Representa relaciones usando la clave primaria
2. StringRelatedField: Usa el método __str__ del modelo relacionado
3. SlugRelatedField: Usa un campo específico del modelo relacionado
4. HyperlinkedRelatedField: Representa relaciones como URLs
5. Nested Serializers: Serializers anidados para representaciones completas

Para relaciones Many-to-Many:
- Podemos usar serializers anidados
- Métodos personalizados para manejar la asignación
- Validación personalizada para relaciones complejas
"""

from rest_framework import serializers
from django.contrib.auth.models import Group, Permission
from django.db import models
from core.crm.models import RolExtendido, PermisoExtendido
from core.users.models import User


class PermisoBasicSerializer(serializers.ModelSerializer):
    """
    📝 MICROCONCEPTO: Serializers para modelos relacionados
    
    Cuando trabajamos con relaciones OneToOne como PermisoExtendido -> Permission,
    podemos acceder a los campos del modelo relacionado directamente.
    """
    
    # Campos del modelo Permission relacionado
    nombre = serializers.CharField(source='permission.name', read_only=True)
    codename = serializers.CharField(source='permission.codename', read_only=True)
    content_type = serializers.CharField(source='permission.content_type.name', read_only=True)
    
    class Meta:
        model = PermisoExtendido
        fields = ['id', 'nombre', 'codename', 'content_type', 'descripcion_detallada', 
                 'modulo', 'activo']


class PermisoDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para permisos con información completa"""
    
    permission_info = serializers.SerializerMethodField()
    
    class Meta:
        model = PermisoExtendido
        fields = ['id', 'permission_info', 'descripcion_detallada', 'modulo', 'activo']
        
    def get_permission_info(self, obj):
        """
        📝 MICROCONCEPTO: SerializerMethodField para datos complejos
        
        Útil cuando necesitamos estructurar datos de manera específica
        o cuando la relación es compleja.
        """
        return {
            'id': obj.permission.id,
            'name': obj.permission.name,
            'codename': obj.permission.codename,
            'content_type': {
                'id': obj.permission.content_type.id,
                'app_label': obj.permission.content_type.app_label,
                'model': obj.permission.content_type.model,
                'name': obj.permission.content_type.name
            }
        }


class RolBasicSerializer(serializers.ModelSerializer):
    """
    Serializer básico para roles con información resumida
    """
    
    # Campos del modelo Group relacionado
    nombre = serializers.CharField(source='group.name', read_only=True)
    usuarios_count = serializers.SerializerMethodField()
    permisos_count = serializers.SerializerMethodField()
    
    class Meta:
        model = RolExtendido
        fields = ['id', 'nombre', 'descripcion', 'activo', 'fecha_creacion',
                 'usuarios_count', 'permisos_count']
        
    def get_usuarios_count(self, obj):
        """Contar usuarios que tienen este rol"""
        return obj.group.user_set_custom.count()
        
    def get_permisos_count(self, obj):
        """Contar permisos asignados a este rol"""
        return obj.group.permissions.count()


class RolDetailSerializer(serializers.ModelSerializer):
    """
    📝 MICROCONCEPTO: Serializers anidados para relaciones complejas
    
    Cuando necesitamos mostrar información detallada de relaciones,
    podemos usar serializers anidados. Esto nos permite controlar
    exactamente qué información se incluye.
    """
    
    nombre = serializers.CharField(source='group.name', read_only=True)
    display_name = serializers.SerializerMethodField()
    nivel_jerarquia = serializers.SerializerMethodField()
    usuarios_count = serializers.SerializerMethodField()
    permisos_count = serializers.SerializerMethodField()
    
    # Serializer anidado para permisos
    permisos = serializers.SerializerMethodField()
    
    class Meta:
        model = RolExtendido
        fields = ['id', 'nombre', 'display_name', 'descripcion', 'activo', 
                 'fecha_creacion', 'nivel_jerarquia', 'usuarios_count', 
                 'permisos_count', 'permisos']
        
    def get_display_name(self, obj):
        """Nombres amigables para mostrar"""
        display_names = {
            'administrador': 'Gerente',
            'empleadonivel1': 'Supervisor',
            'empleadonivel2': 'Vendedor',
            'cliente': 'Cliente'
        }
        return display_names.get(obj.group.name, obj.group.name)
        
    def get_nivel_jerarquia(self, obj):
        """Nivel jerárquico del rol"""
        jerarquia = {
            'administrador': 1,
            'empleadonivel1': 2,
            'empleadonivel2': 3,
            'cliente': 4
        }
        return jerarquia.get(obj.group.name, 5)
        
    def get_usuarios_count(self, obj):
        return obj.group.user_set_custom.count()
        
    def get_permisos_count(self, obj):
        return obj.group.permissions.count()
        
    def get_permisos(self, obj):
        """
        📝 MICROCONCEPTO: Serialización manual de relaciones
        
        A veces necesitamos control total sobre cómo se serializan
        las relaciones. Aquí obtenemos los permisos y los serializamos
        manualmente.
        """
        permisos = []
        for permission in obj.group.permissions.all():
            # Buscar si existe PermisoExtendido para este permission
            try:
                permiso_ext = PermisoExtendido.objects.get(permission=permission)
                permisos.append({
                    'id': permiso_ext.id,
                    'nombre': permission.name,
                    'descripcion': permiso_ext.descripcion_detallada or permission.name,
                    'modulo': permiso_ext.modulo,
                    'activo': permiso_ext.activo
                })
            except PermisoExtendido.DoesNotExist:
                # Si no existe PermisoExtendido, usar datos básicos
                permisos.append({
                    'id': permission.id,
                    'nombre': permission.name,
                    'descripcion': permission.name,
                    'modulo': 'Sistema',
                    'activo': True
                })
        return permisos


class RolPermissionsSerializer(serializers.ModelSerializer):
    """
    Serializer específico para gestionar permisos de un rol
    """
    
    rol = serializers.SerializerMethodField()
    permisos = serializers.SerializerMethodField()
    
    class Meta:
        model = RolExtendido
        fields = ['rol', 'permisos']
        
    def get_rol(self, obj):
        """Información básica del rol"""
        return {
            'id': obj.id,
            'nombre': obj.group.name,
            'descripcion': obj.descripcion
        }
        
    def get_permisos(self, obj):
        """Lista detallada de permisos"""
        permisos = []
        for permission in obj.group.permissions.all():
            try:
                permiso_ext = PermisoExtendido.objects.get(permission=permission)
                permisos.append({
                    'id': permiso_ext.id,
                    'nombre': permission.name,
                    'descripcion': permiso_ext.descripcion_detallada,
                    'modulo': permiso_ext.modulo,
                    'activo': permiso_ext.activo
                })
            except PermisoExtendido.DoesNotExist:
                permisos.append({
                    'id': permission.id,
                    'nombre': permission.name,
                    'descripcion': permission.name,
                    'modulo': 'Sistema',
                    'activo': True
                })
        return permisos


class AssignRoleSerializer(serializers.Serializer):
    """
    📝 MICROCONCEPTO: Serializer para operaciones complejas
    
    Este serializer no está vinculado a un modelo específico,
    sino que maneja una operación compleja: asignar roles a usuarios.
    """
    
    roles = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="Lista de IDs de roles a asignar"
    )
    motivo = serializers.CharField(
        max_length=255,
        required=False,
        help_text="Motivo de la asignación de roles"
    )
    
    def validate_roles(self, value):
        """
        📝 MICROCONCEPTO: Validación de listas
        
        Cuando tenemos un ListField, podemos validar tanto la lista
        como cada elemento individual.
        """
        if not value:
            raise serializers.ValidationError("Debe proporcionar al menos un rol.")
            
        # Validar que todos los roles existen
        existing_roles = RolExtendido.objects.filter(id__in=value, activo=True)
        if len(existing_roles) != len(value):
            invalid_ids = set(value) - set(existing_roles.values_list('id', flat=True))
            raise serializers.ValidationError(
                f"Los siguientes IDs de roles no son válidos: {list(invalid_ids)}"
            )
            
        return value
        
    def validate(self, attrs):
        """Validaciones adicionales"""
        # Aquí podríamos agregar validaciones de negocio
        # Por ejemplo, verificar que el usuario puede asignar estos roles
        return attrs


class UserRoleAssignmentSerializer(serializers.Serializer):
    """
    Serializer para la respuesta de asignación de roles
    """
    
    message = serializers.CharField()
    usuario = serializers.SerializerMethodField()
    
    def get_usuario(self, obj):
        """
        📝 MICROCONCEPTO: Serialización de respuestas personalizadas
        
        obj aquí será un diccionario con 'user' y 'roles_asignados'
        que pasamos desde la vista.
        """
        user = obj['user']
        roles_asignados = obj['roles_asignados']
        
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'roles': [
                {
                    'id': rol.id,
                    'nombre': rol.group.name,
                    'fecha_asignacion': obj.get('fecha_asignacion')
                }
                for rol in roles_asignados
            ]
        }


class UsersByRoleSerializer(serializers.Serializer):
    """
    Serializer para listar usuarios por rol
    """
    
    rol = serializers.SerializerMethodField()
    usuarios = serializers.SerializerMethodField()
    
    def get_rol(self, obj):
        """Información del rol"""
        rol_extendido = obj['rol_extendido']
        return {
            'nombre': rol_extendido.group.name,
            'descripcion': rol_extendido.descripcion,
            'total_usuarios': obj['total_usuarios']
        }
        
    def get_usuarios(self, obj):
        """Lista de usuarios con este rol"""
        usuarios = obj['usuarios']
        return [
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': f"{user.first_name} {user.last_name}".strip(),
                'is_active': user.is_active,
                'fecha_asignacion_rol': obj.get('fecha_asignacion_rol'),
                'last_login': user.last_login
            }
            for user in usuarios
        ]


# === SERIALIZERS PARA PERMISOS ===

class PermissionSerializer(serializers.ModelSerializer):
    """
    Serializer básico para permisos del sistema Django
    """
    content_type_name = serializers.CharField(source='content_type.name', read_only=True)
    app_label = serializers.CharField(source='content_type.app_label', read_only=True)
    model = serializers.CharField(source='content_type.model', read_only=True)
    
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type_name', 'app_label', 'model']


class PermissionDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado para permisos con información completa
    """
    content_type_info = serializers.SerializerMethodField()
    usage_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type_info', 'usage_stats']
    
    def get_content_type_info(self, obj):
        """Información completa del content type"""
        return {
            'id': obj.content_type.id,
            'name': obj.content_type.name,
            'app_label': obj.content_type.app_label,
            'model': obj.content_type.model
        }
    
    def get_usage_stats(self, obj):
        """Estadísticas de uso del permiso"""
        try:
            # Contar cuántos grupos tienen este permiso
            groups_count = obj.group_set.count()
            # Contar cuántos usuarios tienen este permiso (directa o indirectamente)
            users_with_permission = User.objects.filter(
                models.Q(user_permissions=obj) | 
                models.Q(groups__permissions=obj)
            ).distinct().count()
            
            return {
                'groups_count': groups_count,
                'users_with_permission': users_with_permission
            }
        except:
            return {'groups_count': 0, 'users_with_permission': 0}


# === SERIALIZERS PARA OPERACIONES EN LOTE ===

class BulkUserRoleSerializer(serializers.Serializer):
    """
    Serializer para operaciones masivas de asignación de roles
    """
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        help_text="Lista de IDs de usuarios"
    )
    role_id = serializers.IntegerField(help_text="ID del rol a asignar/desasignar")
    
    def validate_user_ids(self, value):
        """Validar que todos los user_ids existan"""
        existing_users = User.objects.filter(id__in=value).values_list('id', flat=True)
        non_existing = set(value) - set(existing_users)
        
        if non_existing:
            raise serializers.ValidationError(
                f"Los siguientes IDs de usuario no existen: {list(non_existing)}"
            )
        
        return value
    
    def validate_role_id(self, value):
        """Validar que el rol exista"""
        try:
            RolExtendido.objects.get(id=value)
        except RolExtendido.DoesNotExist:
            raise serializers.ValidationError("El rol especificado no existe")
        
        return value


class UserRolesSerializer(serializers.Serializer):
    """
    Serializer para mostrar todos los roles de un usuario
    """
    user_info = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    
    def get_user_info(self, obj):
        """Información básica del usuario"""
        return {
            'id': obj.id,
            'username': obj.username,
            'email': obj.email,
            'full_name': f"{obj.first_name} {obj.last_name}".strip(),
            'is_active': obj.is_active
        }
    
    def get_roles(self, obj):
        """Lista de roles del usuario"""
        roles_data = []
        for group in obj.groups.all():
            try:
                rol_extendido = RolExtendido.objects.get(group=group)
                roles_data.append({
                    'id': rol_extendido.id,
                    'name': group.name,
                    'description': rol_extendido.descripcion,
                    'permissions_count': group.permissions.count()
                })
            except RolExtendido.DoesNotExist:
                # Grupo sin extensión CRM
                roles_data.append({
                    'id': None,
                    'name': group.name,
                    'description': 'Grupo de Django estándar',
                    'permissions_count': group.permissions.count()
                })
        
        return roles_data


class RoleUsersSerializer(serializers.Serializer):
    """
    Serializer para mostrar todos los usuarios de un rol
    """
    role_info = serializers.SerializerMethodField()
    users = serializers.SerializerMethodField()
    
    def get_role_info(self, obj):
        """Información básica del rol"""
        return {
            'id': obj.id,
            'name': obj.group.name,
            'description': obj.descripcion,
            'permissions_count': obj.group.permissions.count()
        }
    
    def get_users(self, obj):
        """Lista de usuarios con este rol"""
        users_data = []
        for user in obj.group.user_set.all():
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': f"{user.first_name} {user.last_name}".strip(),
                'is_active': user.is_active,
                'last_login': user.last_login
            })
        
        return users_data
