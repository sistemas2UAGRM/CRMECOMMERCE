# api/v1/crm/services/permission_service.py

"""
🔐 SERVICIO DE PERMISOS - CRM

Servicio de negocio para gestión de permisos:
- Consulta de permisos disponibles
- Agrupación por módulos
- Validaciones de acceso
- Permisos específicos por usuario

Principios aplicados:
- Single Responsibility: Solo gestión de permisos
- Clean Architecture: Lógica de negocio separada
- Security First: Validaciones de seguridad
"""

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from core.crm.models import PermisoExtendido


class PermissionService:
    """
    Servicio para operaciones de permisos del sistema.
    
    Encapsula la lógica de negocio para:
    - Consulta de permisos disponibles
    - Agrupación por aplicaciones/módulos
    - Validaciones de acceso
    - Permisos específicos de usuario
    """
    
    @staticmethod
    def get_all_permissions():
        """
        Obtener todos los permisos disponibles en el sistema.
        
        Returns:
            QuerySet: Permisos ordenados por aplicación y modelo
        """
        return Permission.objects.select_related('content_type').order_by(
            'content_type__app_label',
            'content_type__model',
            'codename'
        )
    
    @staticmethod
    def get_permissions_by_app(app_label):
        """
        Obtener permisos de una aplicación específica.
        
        Args:
            app_label (str): Nombre de la aplicación
            
        Returns:
            QuerySet: Permisos de la aplicación
        """
        return Permission.objects.filter(
            content_type__app_label=app_label
        ).select_related('content_type').order_by(
            'content_type__model',
            'codename'
        )
    
    @staticmethod
    def get_permissions_by_model(app_label, model_name):
        """
        Obtener permisos de un modelo específico.
        
        Args:
            app_label (str): Nombre de la aplicación
            model_name (str): Nombre del modelo
            
        Returns:
            QuerySet: Permisos del modelo
        """
        return Permission.objects.filter(
            content_type__app_label=app_label,
            content_type__model=model_name
        ).select_related('content_type').order_by('codename')
    
    @staticmethod
    def search_permissions(query):
        """
        Buscar permisos por nombre o descripción.
        
        Args:
            query (str): Término de búsqueda
            
        Returns:
            QuerySet: Permisos que coinciden con la búsqueda
        """
        return Permission.objects.filter(
            Q(name__icontains=query) |
            Q(codename__icontains=query) |
            Q(content_type__model__icontains=query)
        ).select_related('content_type').order_by(
            'content_type__app_label',
            'content_type__model',
            'codename'
        )
    
    @staticmethod
    def get_grouped_permissions():
        """
        Obtener permisos agrupados por aplicación y modelo.
        
        Returns:
            dict: Permisos agrupados jerárquicamente
        """
        permissions = PermissionService.get_all_permissions()
        grouped = {}
        
        for permission in permissions:
            app_label = permission.content_type.app_label
            model_name = permission.content_type.model
            
            if app_label not in grouped:
                grouped[app_label] = {}
            
            if model_name not in grouped[app_label]:
                grouped[app_label][model_name] = []
            
            grouped[app_label][model_name].append({
                'id': permission.id,
                'name': permission.name,
                'codename': permission.codename
            })
        
        return grouped
    
    @staticmethod
    def get_user_permissions(user):
        """
        Obtener todos los permisos de un usuario.
        
        Args:
            user: Usuario del cual obtener permisos
            
        Returns:
            QuerySet: Permisos del usuario (directos + por grupos)
        """
        return user.get_all_permissions()
    
    @staticmethod
    def check_user_permission(user, permission_codename):
        """
        Verificar si un usuario tiene un permiso específico.
        
        Args:
            user: Usuario a verificar
            permission_codename (str): Código del permiso
            
        Returns:
            bool: True si tiene el permiso
        """
        return user.has_perm(permission_codename)
    
    @staticmethod
    def get_app_modules():
        """
        Obtener lista de módulos/aplicaciones disponibles.
        
        Returns:
            list: Lista de aplicaciones con permisos
        """
        content_types = ContentType.objects.filter(
            permission__isnull=False
        ).values_list('app_label', flat=True).distinct().order_by('app_label')
        
        return list(content_types)
    
    @staticmethod
    def get_permission_stats():
        """
        Obtener estadísticas de permisos del sistema.
        
        Returns:
            dict: Estadísticas de permisos
        """
        total_permissions = Permission.objects.count()
        total_apps = ContentType.objects.filter(
            permission__isnull=False
        ).values('app_label').distinct().count()
        
        # Permisos por tipo de acción
        action_stats = {}
        actions = ['add', 'change', 'delete', 'view']
        
        for action in actions:
            count = Permission.objects.filter(
                codename__startswith=action
            ).count()
            action_stats[action] = count
        
        return {
            'total_permisos': total_permissions,
            'total_aplicaciones': total_apps,
            'permisos_por_accion': action_stats
        }
    
    @staticmethod
    def validate_permission_access(user_requesting, target_permission):
        """
        Validar que un usuario puede gestionar un permiso específico.
        
        Args:
            user_requesting: Usuario que solicita la operación
            target_permission: Permiso objetivo
            
        Returns:
            bool: True si puede gestionar el permiso
        """
        # Solo administradores pueden gestionar permisos
        if user_requesting.rol == 'administrador':
            return True
        
        # Supervisores pueden gestionar algunos permisos específicos
        if user_requesting.rol == 'empleadonivel1':
            # Definir permisos que pueden gestionar supervisores
            allowed_apps = ['ecommerce', 'common']
            if target_permission.content_type.app_label in allowed_apps:
                return True
        
        return False
    
    @staticmethod
    def get_extended_permissions():
        """
        Obtener permisos extendidos personalizados.
        
        Returns:
            QuerySet: Permisos extendidos
        """
        return PermisoExtendido.objects.filter(activo=True).order_by('nombre')
    
    @staticmethod
    def create_extended_permission(name, description, codename):
        """
        Crear un permiso extendido personalizado.
        
        Args:
            name (str): Nombre del permiso
            description (str): Descripción del permiso
            codename (str): Código único del permiso
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            # Verificar que no existe un permiso con el mismo código
            if PermisoExtendido.objects.filter(codigo=codename).exists():
                return {
                    'success': False,
                    'error': f'Ya existe un permiso con el código "{codename}"'
                }
            
            permission = PermisoExtendido.objects.create(
                nombre=name,
                descripcion=description,
                codigo=codename
            )
            
            return {
                'success': True,
                'permission': permission,
                'mensaje': f'Permiso "{name}" creado exitosamente'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al crear permiso: {str(e)}'
            }
