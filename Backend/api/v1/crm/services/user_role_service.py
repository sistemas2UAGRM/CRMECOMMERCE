# api/v1/crm/services/user_role_service.py

"""
👥 SERVICIO DE USUARIO-ROL - CRM

Servicio de negocio para gestión de asignación de roles:
- Asignación/desasignación de roles a usuarios
- Validaciones jerárquicas
- Consultas por rol
- Auditoría de cambios

Principios aplicados:
- Single Responsibility: Solo gestión usuario-rol
- Clean Architecture: Lógica de negocio separada
- Security First: Validaciones jerárquicas
"""

from django.db import transaction
from django.contrib.auth.models import Group
from django.db.models import Q
from core.users.models import User
from core.crm.models import RolExtendido


class UserRoleService:
    """
    Servicio para operaciones de asignación de roles a usuarios.
    
    Encapsula la lógica de negocio para:
    - Asignación de roles a usuarios
    - Validaciones jerárquicas
    - Consultas por rol
    - Gestión de permisos
    """
    
    @staticmethod
    @transaction.atomic
    def assign_role_to_user(user_id, role_name, requesting_user):
        """
        Asignar un rol a un usuario con validaciones.
        
        Args:
            user_id (int): ID del usuario
            role_name (str): Nombre del rol
            requesting_user: Usuario que solicita la asignación
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            # Validar que el usuario existe
            user = User.objects.get(id=user_id)
            
            # Validar que el rol existe
            try:
                group = Group.objects.get(name=role_name)
                rol_extendido = RolExtendido.objects.get(group=group)
            except (Group.DoesNotExist, RolExtendido.DoesNotExist):
                return {
                    'success': False,
                    'error': f'Rol "{role_name}" no encontrado'
                }
            
            # Validar jerarquía de permisos
            if not UserRoleService._validate_role_assignment(requesting_user, role_name):
                return {
                    'success': False,
                    'error': 'No tienes permisos para asignar este rol'
                }
            
            # Verificar si ya tiene el rol
            if user.groups.filter(name=role_name).exists():
                return {
                    'success': False,
                    'error': f'El usuario ya tiene el rol "{role_name}"'
                }
            
            # Asignar rol
            user.groups.add(group)
            
            # Actualizar campo rol en el modelo User si es necesario
            user.rol = role_name
            user.save()
            
            return {
                'success': True,
                'mensaje': f'Rol "{role_name}" asignado a {user.username}',
                'user': user,
                'role': role_name
            }
            
        except User.DoesNotExist:
            return {
                'success': False,
                'error': 'Usuario no encontrado'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al asignar rol: {str(e)}'
            }
    
    @staticmethod
    @transaction.atomic
    def remove_role_from_user(user_id, role_name, requesting_user):
        """
        Remover un rol de un usuario.
        
        Args:
            user_id (int): ID del usuario
            role_name (str): Nombre del rol
            requesting_user: Usuario que solicita la remoción
            
        Returns:
            dict: Resultado de la operación
        """
        try:
            user = User.objects.get(id=user_id)
            
            # Validar jerarquía de permisos
            if not UserRoleService._validate_role_assignment(requesting_user, role_name):
                return {
                    'success': False,
                    'error': 'No tienes permisos para remover este rol'
                }
            
            # Verificar que tiene el rol
            try:
                group = Group.objects.get(name=role_name)
                if not user.groups.filter(name=role_name).exists():
                    return {
                        'success': False,
                        'error': f'El usuario no tiene el rol "{role_name}"'
                    }
            except Group.DoesNotExist:
                return {
                    'success': False,
                    'error': f'Rol "{role_name}" no encontrado'
                }
            
            # Remover rol
            user.groups.remove(group)
            
            # Actualizar campo rol si es necesario
            remaining_roles = user.groups.all()
            if remaining_roles.exists():
                user.rol = remaining_roles.first().name
            else:
                user.rol = 'cliente'  # Rol por defecto
            user.save()
            
            return {
                'success': True,
                'mensaje': f'Rol "{role_name}" removido de {user.username}',
                'user': user
            }
            
        except User.DoesNotExist:
            return {
                'success': False,
                'error': 'Usuario no encontrado'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al remover rol: {str(e)}'
            }
    
    @staticmethod
    def get_users_by_role(role_name):
        """
        Obtener usuarios que tienen un rol específico.
        
        Args:
            role_name (str): Nombre del rol
            
        Returns:
            QuerySet: Usuarios con el rol especificado
        """
        try:
            group = Group.objects.get(name=role_name)
            return group.user_set.all().order_by('username')
        except Group.DoesNotExist:
            return User.objects.none()
    
    @staticmethod
    def get_user_roles(user_id):
        """
        Obtener todos los roles de un usuario.
        
        Args:
            user_id (int): ID del usuario
            
        Returns:
            QuerySet: Roles del usuario
        """
        try:
            user = User.objects.get(id=user_id)
            return user.groups.all().order_by('name')
        except User.DoesNotExist:
            return Group.objects.none()
    
    @staticmethod
    def search_users_by_role_and_name(role_name=None, user_query=None):
        """
        Buscar usuarios por rol y/o nombre.
        
        Args:
            role_name (str, optional): Filtrar por rol
            user_query (str, optional): Búsqueda en nombre/email
            
        Returns:
            QuerySet: Usuarios que coinciden con los criterios
        """
        queryset = User.objects.all()
        
        if role_name:
            queryset = queryset.filter(groups__name=role_name)
        
        if user_query:
            queryset = queryset.filter(
                Q(username__icontains=user_query) |
                Q(first_name__icontains=user_query) |
                Q(last_name__icontains=user_query) |
                Q(email__icontains=user_query)
            )
        
        return queryset.distinct().order_by('username')
    
    @staticmethod
    def get_role_statistics():
        """
        Obtener estadísticas de asignación de roles.
        
        Returns:
            dict: Estadísticas por rol
        """
        roles = RolExtendido.objects.all()
        stats = {}
        
        total_users = User.objects.count()
        users_with_roles = User.objects.filter(groups__isnull=False).distinct().count()
        users_without_roles = total_users - users_with_roles
        
        stats['resumen'] = {
            'total_usuarios': total_users,
            'usuarios_con_roles': users_with_roles,
            'usuarios_sin_roles': users_without_roles
        }
        
        stats['por_rol'] = []
        for rol in roles:
            user_count = rol.group.user_set.count()
            stats['por_rol'].append({
                'rol': rol.group.name,
                'descripcion': rol.descripcion,
                'usuarios': user_count,
                'activo': rol.activo
            })
        
        return stats
    
    @staticmethod
    def bulk_assign_role(user_ids, role_name, requesting_user):
        """
        Asignar un rol a múltiples usuarios.
        
        Args:
            user_ids (list): Lista de IDs de usuarios
            role_name (str): Nombre del rol
            requesting_user: Usuario que solicita la asignación
            
        Returns:
            dict: Resultado de la operación masiva
        """
        # Validar jerarquía de permisos
        if not UserRoleService._validate_role_assignment(requesting_user, role_name):
            return {
                'success': False,
                'error': 'No tienes permisos para asignar este rol'
            }
        
        try:
            group = Group.objects.get(name=role_name)
        except Group.DoesNotExist:
            return {
                'success': False,
                'error': f'Rol "{role_name}" no encontrado'
            }
        
        results = {
            'success': True,
            'asignados': [],
            'errores': [],
            'ya_tenian_rol': []
        }
        
        with transaction.atomic():
            for user_id in user_ids:
                try:
                    user = User.objects.get(id=user_id)
                    
                    if user.groups.filter(name=role_name).exists():
                        results['ya_tenian_rol'].append(user.username)
                    else:
                        user.groups.add(group)
                        user.rol = role_name
                        user.save()
                        results['asignados'].append(user.username)
                        
                except User.DoesNotExist:
                    results['errores'].append(f'Usuario ID {user_id} no encontrado')
                except Exception as e:
                    results['errores'].append(f'Error con usuario ID {user_id}: {str(e)}')
        
        return results
    
    @staticmethod
    def _validate_role_assignment(requesting_user, target_role_name):
        """
        Validar que un usuario puede asignar un rol específico.
        
        Args:
            requesting_user: Usuario que solicita la operación
            target_role_name (str): Nombre del rol objetivo
            
        Returns:
            bool: True si puede asignar el rol
        """
        # Los administradores pueden asignar cualquier rol
        if requesting_user.rol == 'administrador':
            return True
        
        # Los supervisores pueden asignar roles de nivel inferior
        if requesting_user.rol == 'empleadonivel1':
            restricted_roles = ['administrador', 'empleadonivel1']
            return target_role_name not in restricted_roles
        
        # Otros usuarios no pueden asignar roles
        return False
    
    @staticmethod
    def get_assignable_roles(requesting_user):
        """
        Obtener roles que un usuario puede asignar según su jerarquía.
        
        Args:
            requesting_user: Usuario que solicita la lista
            
        Returns:
            QuerySet: Roles que puede asignar
        """
        if requesting_user.rol == 'administrador':
            # Administradores pueden asignar cualquier rol
            return RolExtendido.objects.filter(activo=True).order_by('group__name')
        elif requesting_user.rol == 'empleadonivel1':
            # Supervisores pueden asignar roles excepto admin y supervisor
            restricted_roles = ['administrador', 'empleadonivel1']
            return RolExtendido.objects.filter(
                activo=True
            ).exclude(
                group__name__in=restricted_roles
            ).order_by('group__name')
        else:
            # Otros usuarios no pueden asignar roles
            return RolExtendido.objects.none()
