# api/v1/crm/services/role_service.py

"""
👑 SERVICIO DE ROLES - CRM

Servicio de negocio para gestión de roles:
- CRUD de roles del sistema
- Gestión de permisos por rol
- Validaciones de integridad
- Auditoría de cambios

Principios aplicados:
- Single Responsibility: Solo gestión de roles
- Clean Architecture: Lógica de negocio separada
- Transaction Safety: Operaciones atómicas
"""

from django.db import transaction
from django.contrib.auth.models import Group, Permission
from django.db.models import Count, Q
from core.crm.models import RolExtendido, PermisoExtendido
from core.users.models import User


class RoleService:
    """
    Servicio para operaciones de roles y sus permisos.
    
    Encapsula la lógica de negocio para:
    - Gestión CRUD de roles
    - Asignación de permisos a roles
    - Validaciones de integridad
    - Consultas jerárquicas
    """
    
    @staticmethod
    def get_roles_with_stats():
        """
        Obtener roles con estadísticas de usuarios asignados.
        
        Returns:
            QuerySet: Roles con conteo de usuarios
        """
        return RolExtendido.objects.annotate(
            total_usuarios=Count('group__user')
        ).order_by('group__name')
    
    @staticmethod
    def create_role(name, description=None, permissions=None):
        """
        Crear un nuevo rol con permisos opcionales.
        
        Args:
            name (str): Nombre del rol
            description (str, optional): Descripción del rol
            permissions (list, optional): Lista de IDs de permisos
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            with transaction.atomic():
                # Verificar que no existe un rol con el mismo nombre
                if Group.objects.filter(name=name).exists():
                    return {
                        'success': False,
                        'error': f'Ya existe un rol con el nombre "{name}"'
                    }
                
                # Crear grupo de Django
                group = Group.objects.create(name=name)
                
                # Crear rol extendido
                rol = RolExtendido.objects.create(
                    descripcion=description or '',
                    group=group
                )
                
                # Asignar permisos si se proporcionaron
                if permissions:
                    RoleService._assign_permissions_to_role(rol, permissions)
                
                return {
                    'success': True,
                    'rol': rol,
                    'mensaje': f'Rol "{name}" creado exitosamente'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al crear rol: {str(e)}'
            }
    
    @staticmethod
    @transaction.atomic
    def update_role(role_id, name=None, description=None, permissions=None):
        """
        Actualizar un rol existente.
        
        Args:
            role_id (int): ID del rol
            name (str, optional): Nuevo nombre
            description (str, optional): Nueva descripción
            permissions (list, optional): Nueva lista de permisos
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            rol = RolExtendido.objects.get(id=role_id)
            
            # Actualizar nombre si se proporciona
            if name and name != rol.group.name:
                # Verificar que no existe otro rol con el mismo nombre
                if Group.objects.filter(name=name).exclude(id=rol.group.id).exists():
                    return {
                        'success': False,
                        'error': f'Ya existe un rol con el nombre "{name}"'
                    }
                
                rol.group.name = name
                rol.group.save()
            
            # Actualizar descripción si se proporciona
            if description is not None:
                rol.descripcion = description
            
            rol.save()
            
            # Actualizar permisos si se proporcionan
            if permissions is not None:
                RoleService._assign_permissions_to_role(rol, permissions)
            
            return {
                'success': True,
                'rol': rol,
                'mensaje': f'Rol "{rol.group.name}" actualizado exitosamente'
            }
            
        except RolExtendido.DoesNotExist:
            return {
                'success': False,
                'error': 'Rol no encontrado'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al actualizar rol: {str(e)}'
            }
    
    @staticmethod
    @transaction.atomic
    def delete_role(role_id):
        """
        Eliminar un rol del sistema.
        
        Args:
            role_id (int): ID del rol
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            rol = RolExtendido.objects.get(id=role_id)
            
            # Verificar que no hay usuarios asignados
            if rol.group.user_set.exists():
                return {
                    'success': False,
                    'error': 'No se puede eliminar un rol que tiene usuarios asignados'
                }
            
            rol_nombre = rol.group.name
            
            # Eliminar grupo asociado (cascada eliminará el rol)
            rol.group.delete()
            
            return {
                'success': True,
                'mensaje': f'Rol "{rol_nombre}" eliminado exitosamente'
            }
            
        except RolExtendido.DoesNotExist:
            return {
                'success': False,
                'error': 'Rol no encontrado'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al eliminar rol: {str(e)}'
            }
    
    @staticmethod
    def get_role_permissions(role_id):
        """
        Obtener permisos asignados a un rol.
        
        Args:
            role_id (int): ID del rol
            
        Returns:
            QuerySet: Permisos del rol
        """
        try:
            rol = RolExtendido.objects.get(id=role_id)
            return rol.group.permissions.all()
        except RolExtendido.DoesNotExist:
            return Permission.objects.none()
    
    @staticmethod
    def get_role_users(role_id):
        """
        Obtener usuarios asignados a un rol.
        
        Args:
            role_id (int): ID del rol
            
        Returns:
            QuerySet: Usuarios del rol
        """
        try:
            rol = RolExtendido.objects.get(id=role_id)
            return rol.group.user_set.all()
        except RolExtendido.DoesNotExist:
            return User.objects.none()
    
    @staticmethod
    def search_roles(query):
        """
        Buscar roles por nombre o descripción.
        
        Args:
            query (str): Término de búsqueda
            
        Returns:
            QuerySet: Roles que coinciden con la búsqueda
        """
        return RolExtendido.objects.filter(
            Q(group__name__icontains=query) |
            Q(descripcion__icontains=query)
        ).annotate(
            total_usuarios=Count('group__user')
        ).order_by('group__name')
    
    @staticmethod
    def _assign_permissions_to_role(rol, permission_ids):
        """
        Asignar permisos a un rol.
        
        Args:
            rol (RolExtendido): Rol al que asignar permisos
            permission_ids (list): Lista de IDs de permisos
        """
        # Limpiar permisos existentes
        rol.group.permissions.clear()
        
        # Asignar nuevos permisos
        if permission_ids:
            permissions = Permission.objects.filter(id__in=permission_ids)
            rol.group.permissions.set(permissions)
    
    @staticmethod
    def get_available_permissions():
        """
        Obtener todos los permisos disponibles en el sistema.
        
        Returns:
            QuerySet: Permisos disponibles agrupados por modelo
        """
        return Permission.objects.select_related('content_type').order_by(
            'content_type__app_label',
            'content_type__model',
            'codename'
        )
    
    @staticmethod
    def validate_role_hierarchy(user_requesting, target_role_name):
        """
        Validar que un usuario puede gestionar un rol específico.
        
        Args:
            user_requesting: Usuario que solicita la operación
            target_role_name (str): Nombre del rol objetivo
            
        Returns:
            bool: True si puede gestionar el rol
        """
        # Los administradores pueden gestionar cualquier rol
        if user_requesting.rol == 'administrador':
            return True
        
        # Los supervisores pueden gestionar roles de nivel inferior
        if user_requesting.rol == 'empleadonivel1':
            restricted_roles = ['administrador', 'empleadonivel1']
            return target_role_name not in restricted_roles
        
        # Otros usuarios no pueden gestionar roles
        return False
