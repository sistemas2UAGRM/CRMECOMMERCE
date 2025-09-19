# api/v1/common/services/bitacora_service.py

"""
📊 SERVICIO DE BITÁCORA - AUDITORÍA SISTEMÁTICA

Este servicio centraliza toda la lógica de negocio relacionada con la bitácora:
- Creación automática de registros de auditoría
- Consultas optimizadas con filtros complejos
- Validaciones de permisos por jerarquía
- Gestión de grandes volúmenes de datos

Casos de uso implementados:
- CU-CM01: Registro automático de acciones de usuario
- CU-CM02: Consulta de bitácora con filtros avanzados
- CU-CM03: Control de acceso por roles
"""

from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from typing import Dict, List, Optional, Any

from core.common.models import Bitacora

User = get_user_model()


class BitacoraService:
    """
    Servicio centralizado para gestión de bitácora y auditoría
    """
    
    @staticmethod
    def create_audit_log(
        usuario: User,
        accion: str,
        detalles: str = '',
        ip: str = '',
        objeto_id: Optional[int] = None,
        objeto_tipo: str = ''
    ) -> Dict[str, Any]:
        """
        CU-CM01: Crear registro de auditoría de forma automática.
        
        Args:
            usuario: Usuario que realiza la acción
            accion: Descripción de la acción realizada
            detalles: Detalles adicionales (JSON o texto)
            ip: Dirección IP del usuario
            objeto_id: ID del objeto modificado (opcional)
            objeto_tipo: Tipo de objeto modificado (opcional)
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            bitacora = Bitacora.objects.create(
                usuario=usuario,
                accion=accion,
                detalles=detalles,
                ip=ip,
                fecha=timezone.now(),
                objeto_id=objeto_id,
                objeto_tipo=objeto_tipo
            )
            
            return {
                'success': True,
                'bitacora': bitacora,
                'mensaje': f'Registro de auditoría creado: {accion}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al crear registro de auditoría: {str(e)}'
            }
    
    @staticmethod
    def get_user_queryset_by_permissions(user: User):
        """
        CU-CM03: Obtener queryset filtrado según permisos del usuario.
        
        Implementa la jerarquía de permisos:
        - Administradores: Ven todo
        - Supervisores (empleadonivel1): Ven su equipo + sus acciones
        - Vendedores (empleadonivel2): Solo sus acciones
        - Clientes: Sin acceso
        
        Args:
            user: Usuario solicitante
            
        Returns:
            QuerySet filtrado según permisos
        """
        if not user.is_authenticated:
            return Bitacora.objects.none()
        
        user_groups = user.groups.values_list('name', flat=True)
        base_queryset = Bitacora.objects.select_related('usuario').order_by('-fecha')
        
        if 'administrador' in user_groups:
            # Administradores ven todo
            return base_queryset
            
        elif 'empleadonivel1' in user_groups:
            # Supervisores ven su equipo (vendedores) + sus propias acciones
            vendedores = User.objects.filter(groups__name='empleadonivel2')
            return base_queryset.filter(
                Q(usuario=user) | Q(usuario__in=vendedores)
            )
            
        elif 'empleadonivel2' in user_groups:
            # Vendedores solo ven sus propias acciones
            return base_queryset.filter(usuario=user)
            
        else:
            # Otros roles (clientes) no tienen acceso
            return Bitacora.objects.none()
    
    @staticmethod
    def apply_advanced_filters(queryset, filters: Dict[str, Any]):
        """
        CU-CM02: Aplicar filtros avanzados a consultas de bitácora.
        
        Args:
            queryset: QuerySet base
            filters: Diccionario con filtros a aplicar
            
        Returns:
            QuerySet filtrado
        """
        # Filtro por rango de fechas
        if filters.get('fecha_inicio'):
            try:
                fecha_inicio = datetime.fromisoformat(
                    filters['fecha_inicio'].replace('Z', '+00:00')
                )
                queryset = queryset.filter(fecha__gte=fecha_inicio)
            except ValueError:
                pass  # Ignorar formato inválido
        
        if filters.get('fecha_fin'):
            try:
                fecha_fin = datetime.fromisoformat(
                    filters['fecha_fin'].replace('Z', '+00:00')
                )
                queryset = queryset.filter(fecha__lte=fecha_fin)
            except ValueError:
                pass
        
        # Filtro por usuario específico
        if filters.get('usuario_id'):
            try:
                queryset = queryset.filter(usuario_id=int(filters['usuario_id']))
            except (ValueError, TypeError):
                pass
        
        # Filtro por acción (búsqueda parcial)
        if filters.get('accion_contiene'):
            queryset = queryset.filter(accion__icontains=filters['accion_contiene'])
        
        # Filtro por IP
        if filters.get('ip'):
            queryset = queryset.filter(ip=filters['ip'])
        
        # Filtro por tipo de objeto
        if filters.get('objeto_tipo'):
            queryset = queryset.filter(objeto_tipo=filters['objeto_tipo'])
        
        # Filtro por ID de objeto
        if filters.get('objeto_id'):
            try:
                queryset = queryset.filter(objeto_id=int(filters['objeto_id']))
            except (ValueError, TypeError):
                pass
        
        # Filtro por búsqueda en detalles
        if filters.get('detalles_contiene'):
            queryset = queryset.filter(detalles__icontains=filters['detalles_contiene'])
        
        return queryset
    
    @staticmethod
    def get_recent_activity(user: User, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Obtener actividad reciente del usuario o su equipo.
        
        Args:
            user: Usuario solicitante
            hours: Horas hacia atrás a consultar
            
        Returns:
            Lista de actividades recientes
        """
        time_threshold = timezone.now() - timedelta(hours=hours)
        queryset = BitacoraService.get_user_queryset_by_permissions(user)
        
        recent_activity = queryset.filter(
            fecha__gte=time_threshold
        ).select_related('usuario')[:50]  # Limitar a 50 registros
        
        activity_list = []
        for registro in recent_activity:
            activity_list.append({
                'id': registro.id,
                'usuario': registro.usuario.username,
                'accion': registro.accion,
                'fecha': registro.fecha,
                'ip': registro.ip,
                'tiempo_transcurrido': (timezone.now() - registro.fecha).total_seconds() / 3600  # En horas
            })
        
        return activity_list
    
    @staticmethod
    def search_audit_logs(
        user: User,
        search_term: str,
        search_fields: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Búsqueda avanzada en registros de auditoría.
        
        Args:
            user: Usuario solicitante
            search_term: Término de búsqueda
            search_fields: Campos donde buscar ['accion', 'detalles', 'usuario__username']
            
        Returns:
            Lista de registros encontrados
        """
        if not search_term.strip():
            return []
        
        if search_fields is None:
            search_fields = ['accion', 'detalles', 'usuario__username']
        
        queryset = BitacoraService.get_user_queryset_by_permissions(user)
        
        # Construir filtro de búsqueda
        search_query = Q()
        for field in search_fields:
            search_query |= Q(**{f"{field}__icontains": search_term})
        
        results = queryset.filter(search_query).select_related('usuario')[:100]
        
        search_results = []
        for registro in results:
            search_results.append({
                'id': registro.id,
                'usuario': registro.usuario.username,
                'accion': registro.accion,
                'detalles': registro.detalles,
                'fecha': registro.fecha,
                'ip': registro.ip,
                'relevancia': BitacoraService._calculate_relevance(registro, search_term)
            })
        
        # Ordenar por relevancia
        search_results.sort(key=lambda x: x['relevancia'], reverse=True)
        
        return search_results
    
    @staticmethod
    def _calculate_relevance(registro: Bitacora, search_term: str) -> float:
        """
        Calcular relevancia de un registro para un término de búsqueda.
        
        Args:
            registro: Registro de bitácora
            search_term: Término buscado
            
        Returns:
            Puntuación de relevancia (0-1)
        """
        term_lower = search_term.lower()
        relevance = 0.0
        
        # Búsqueda en acción (peso alto)
        if term_lower in registro.accion.lower():
            relevance += 0.5
        
        # Búsqueda en detalles (peso medio)
        if registro.detalles and term_lower in registro.detalles.lower():
            relevance += 0.3
        
        # Búsqueda en usuario (peso bajo)
        if term_lower in registro.usuario.username.lower():
            relevance += 0.2
        
        return min(relevance, 1.0)  # Máximo 1.0
    
    @staticmethod
    def get_user_activity_summary(
        user: User,
        target_user_id: Optional[int] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Obtener resumen de actividad de un usuario específico.
        
        Args:
            user: Usuario solicitante (debe tener permisos)
            target_user_id: ID del usuario a consultar (None = usuario actual)
            days: Días hacia atrás a consultar
            
        Returns:
            Diccionario con resumen de actividad
        """
        if target_user_id is None:
            target_user_id = user.id
        
        # Verificar permisos
        queryset = BitacoraService.get_user_queryset_by_permissions(user)
        
        try:
            target_user = User.objects.get(id=target_user_id)
        except User.DoesNotExist:
            return {'error': 'Usuario no encontrado'}
        
        # Verificar que el usuario solicitante puede ver la actividad del usuario objetivo
        test_query = queryset.filter(usuario=target_user)
        if not test_query.exists() and queryset.filter(usuario=target_user).count() == 0:
            return {'error': 'Sin permisos para ver actividad de este usuario'}
        
        time_threshold = timezone.now() - timedelta(days=days)
        
        # Obtener registros del período
        user_logs = queryset.filter(
            usuario=target_user,
            fecha__gte=time_threshold
        )
        
        # Calcular estadísticas
        total_actions = user_logs.count()
        actions_by_day = {}
        action_types = {}
        
        for log in user_logs:
            # Agrupar por día
            day_key = log.fecha.strftime('%Y-%m-%d')
            actions_by_day[day_key] = actions_by_day.get(day_key, 0) + 1
            
            # Agrupar por tipo de acción
            action_key = log.accion.split()[0] if log.accion else 'Unknown'
            action_types[action_key] = action_types.get(action_key, 0) + 1
        
        return {
            'usuario': {
                'id': target_user.id,
                'username': target_user.username,
                'nombre_completo': f"{target_user.first_name} {target_user.last_name}".strip()
            },
            'periodo': {
                'dias': days,
                'fecha_inicio': time_threshold.isoformat(),
                'fecha_fin': timezone.now().isoformat()
            },
            'estadisticas': {
                'total_acciones': total_actions,
                'promedio_diario': round(total_actions / days, 2),
                'acciones_por_dia': actions_by_day,
                'tipos_de_accion': action_types
            }
        }
    
    @staticmethod
    def validate_export_request(user: User, queryset_count: int) -> Dict[str, Any]:
        """
        Validar si un usuario puede exportar datos y si el volumen es apropiado.
        
        Args:
            user: Usuario solicitante
            queryset_count: Cantidad de registros a exportar
            
        Returns:
            Diccionario con resultado de validación
        """
        # Solo administradores pueden exportar
        if not user.groups.filter(name='administrador').exists():
            return {
                'valid': False,
                'error': 'Solo administradores pueden exportar datos de bitácora'
            }
        
        # Verificar límites de exportación
        MAX_EXPORT_RECORDS = 10000
        
        if queryset_count > MAX_EXPORT_RECORDS:
            return {
                'valid': False,
                'error': f'Demasiados registros para exportar ({queryset_count}). '
                        f'El límite es {MAX_EXPORT_RECORDS}. Use filtros para reducir el conjunto.'
            }
        
        if queryset_count == 0:
            return {
                'valid': False,
                'error': 'No hay registros que coincidan con los filtros especificados'
            }
        
        return {
            'valid': True,
            'count': queryset_count,
            'message': f'Exportación válida: {queryset_count} registros'
        }
