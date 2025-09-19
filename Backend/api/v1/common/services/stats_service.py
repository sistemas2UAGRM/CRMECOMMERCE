# api/v1/common/services/stats_service.py

"""
📈 SERVICIO DE ESTADÍSTICAS - ANÁLISIS DE DATOS

Este servicio centraliza toda la lógica de generación de estadísticas:
- Métricas de actividad del sistema
- Análisis de tendencias
- Reportes por períodos
- Estadísticas por usuarios y roles

Casos de uso implementados:
- CU-CM04: Generación de estadísticas del sistema
- CU-CM05: Análisis de actividad por períodos
- CU-CM06: Reportes de uso por usuario/rol
"""

from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from typing import Dict, List, Any

from core.common.models import Bitacora

User = get_user_model()


class StatsService:
    """
    Servicio centralizado para generación de estadísticas y métricas
    """
    
    @staticmethod
    def get_system_overview_stats() -> Dict[str, Any]:
        """
        CU-CM04: Obtener estadísticas generales del sistema.
        
        Returns:
            Diccionario con métricas principales del sistema
        """
        now = timezone.now()
        
        # Definir períodos
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=7)
        month_start = today_start - timedelta(days=30)
        
        # Consultas base
        all_logs = Bitacora.objects.all()
        today_logs = all_logs.filter(fecha__gte=today_start)
        week_logs = all_logs.filter(fecha__gte=week_start)
        month_logs = all_logs.filter(fecha__gte=month_start)
        
        # Estadísticas básicas
        stats = {
            'resumen_general': {
                'total_registros': all_logs.count(),
                'registros_hoy': today_logs.count(),
                'registros_semana': week_logs.count(),
                'registros_mes': month_logs.count()
            },
            'usuarios_activos': {
                'hoy': today_logs.values('usuario').distinct().count(),
                'semana': week_logs.values('usuario').distinct().count(),
                'mes': month_logs.values('usuario').distinct().count()
            },
            'acciones_populares': StatsService._get_popular_actions(week_logs),
            'tendencias': StatsService._get_activity_trends(month_logs),
            'distribucion_por_hora': StatsService._get_hourly_distribution(today_logs)
        }
        
        return stats
    
    @staticmethod
    def get_user_activity_stats(days: int = 30) -> List[Dict[str, Any]]:
        """
        CU-CM06: Obtener estadísticas de actividad por usuario.
        
        Args:
            days: Número de días hacia atrás a analizar
            
        Returns:
            Lista de usuarios con sus estadísticas
        """
        time_threshold = timezone.now() - timedelta(days=days)
        
        # Obtener usuarios con actividad en el período
        user_stats = Bitacora.objects.filter(
            fecha__gte=time_threshold
        ).values(
            'usuario__id',
            'usuario__username', 
            'usuario__first_name',
            'usuario__last_name'
        ).annotate(
            total_acciones=Count('id')
        ).order_by('-total_acciones')
        
        # Enriquecer con detalles adicionales
        detailed_stats = []
        for stat in user_stats:
            user_id = stat['usuario__id']
            
            # Obtener tipos de acciones del usuario
            user_actions = Bitacora.objects.filter(
                usuario_id=user_id,
                fecha__gte=time_threshold
            ).values('accion').annotate(
                count=Count('id')
            ).order_by('-count')[:5]  # Top 5 acciones
            
            # Calcular actividad por día
            daily_activity = StatsService._get_user_daily_activity(user_id, days)
            
            detailed_stats.append({
                'usuario': {
                    'id': user_id,
                    'username': stat['usuario__username'],
                    'nombre_completo': f"{stat['usuario__first_name']} {stat['usuario__last_name']}".strip()
                },
                'actividad': {
                    'total_acciones': stat['total_acciones'],
                    'promedio_diario': round(stat['total_acciones'] / days, 2),
                    'acciones_principales': list(user_actions),
                    'actividad_por_dia': daily_activity
                }
            })
        
        return detailed_stats
    
    @staticmethod
    def get_period_comparison_stats(
        period1_days: int = 7,
        period2_days: int = 14
    ) -> Dict[str, Any]:
        """
        CU-CM05: Comparar estadísticas entre dos períodos.
        
        Args:
            period1_days: Días del período más reciente
            period2_days: Días del período anterior para comparar
            
        Returns:
            Diccionario con comparación de períodos
        """
        now = timezone.now()
        
        # Definir períodos
        period1_start = now - timedelta(days=period1_days)
        period2_start = now - timedelta(days=period2_days)
        period2_end = period1_start
        
        # Obtener datos de cada período
        period1_logs = Bitacora.objects.filter(fecha__gte=period1_start)
        period2_logs = Bitacora.objects.filter(
            fecha__gte=period2_start,
            fecha__lt=period2_end
        )
        
        # Calcular métricas para cada período
        period1_stats = {
            'total_registros': period1_logs.count(),
            'usuarios_activos': period1_logs.values('usuario').distinct().count(),
            'acciones_promedio_diario': period1_logs.count() / period1_days
        }
        
        period2_stats = {
            'total_registros': period2_logs.count(),
            'usuarios_activos': period2_logs.values('usuario').distinct().count(),
            'acciones_promedio_diario': period2_logs.count() / period1_days  # Mismo período para comparar
        }
        
        # Calcular cambios porcentuales
        def calculate_change(current, previous):
            if previous == 0:
                return 100 if current > 0 else 0
            return round(((current - previous) / previous) * 100, 2)
        
        return {
            'periodo_actual': {
                'dias': period1_days,
                'estadisticas': period1_stats
            },
            'periodo_anterior': {
                'dias': period1_days,
                'estadisticas': period2_stats
            },
            'cambios': {
                'total_registros': calculate_change(
                    period1_stats['total_registros'],
                    period2_stats['total_registros']
                ),
                'usuarios_activos': calculate_change(
                    period1_stats['usuarios_activos'],
                    period2_stats['usuarios_activos']
                ),
                'acciones_promedio_diario': calculate_change(
                    period1_stats['acciones_promedio_diario'],
                    period2_stats['acciones_promedio_diario']
                )
            }
        }
    
    @staticmethod
    def get_role_based_stats() -> Dict[str, Any]:
        """
        Obtener estadísticas agrupadas por roles de usuario.
        
        Returns:
            Diccionario con estadísticas por rol
        """
        # Obtener usuarios con sus roles
        users_with_roles = User.objects.prefetch_related('groups').all()
        
        role_stats = {}
        
        for user in users_with_roles:
            user_groups = user.groups.values_list('name', flat=True)
            
            # Clasificar usuario por rol principal
            primary_role = 'sin_rol'
            if 'administrador' in user_groups:
                primary_role = 'administrador'
            elif 'empleadonivel1' in user_groups:
                primary_role = 'supervisor'
            elif 'empleadonivel2' in user_groups:
                primary_role = 'vendedor'
            elif 'cliente' in user_groups:
                primary_role = 'cliente'
            
            # Inicializar estadísticas del rol si no existe
            if primary_role not in role_stats:
                role_stats[primary_role] = {
                    'total_usuarios': 0,
                    'usuarios_activos_mes': 0,
                    'total_acciones_mes': 0,
                    'promedio_acciones_por_usuario': 0
                }
            
            role_stats[primary_role]['total_usuarios'] += 1
            
            # Calcular actividad del último mes
            month_ago = timezone.now() - timedelta(days=30)
            user_activity = Bitacora.objects.filter(
                usuario=user,
                fecha__gte=month_ago
            )
            
            if user_activity.exists():
                role_stats[primary_role]['usuarios_activos_mes'] += 1
                role_stats[primary_role]['total_acciones_mes'] += user_activity.count()
        
        # Calcular promedios
        for role, stats in role_stats.items():
            if stats['usuarios_activos_mes'] > 0:
                stats['promedio_acciones_por_usuario'] = round(
                    stats['total_acciones_mes'] / stats['usuarios_activos_mes'], 2
                )
        
        return role_stats
    
    @staticmethod
    def _get_popular_actions(queryset) -> List[Dict[str, Any]]:
        """
        Obtener las acciones más populares de un queryset.
        
        Args:
            queryset: QuerySet de Bitacora
            
        Returns:
            Lista de acciones ordenadas por frecuencia
        """
        popular_actions = queryset.values('accion').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        return [
            {
                'accion': action['accion'],
                'cantidad': action['count']
            }
            for action in popular_actions
        ]
    
    @staticmethod
    def _get_activity_trends(queryset) -> Dict[str, List[Dict[str, Any]]]:
        """
        Obtener tendencias de actividad por día.
        
        Args:
            queryset: QuerySet de Bitacora
            
        Returns:
            Diccionario con tendencias diarias
        """
        # Agrupar por día
        daily_counts = {}
        
        for log in queryset:
            day_key = log.fecha.strftime('%Y-%m-%d')
            daily_counts[day_key] = daily_counts.get(day_key, 0) + 1
        
        # Convertir a lista ordenada
        daily_trends = []
        for day, count in sorted(daily_counts.items()):
            daily_trends.append({
                'fecha': day,
                'acciones': count
            })
        
        return {
            'actividad_diaria': daily_trends,
            'total_dias': len(daily_trends),
            'promedio_diario': sum(daily_counts.values()) / len(daily_counts) if daily_counts else 0
        }
    
    @staticmethod
    def _get_hourly_distribution(queryset) -> List[Dict[str, Any]]:
        """
        Obtener distribución de actividad por hora del día.
        
        Args:
            queryset: QuerySet de Bitacora
            
        Returns:
            Lista con actividad por hora
        """
        hourly_counts = {}
        
        for log in queryset:
            hour = log.fecha.hour
            hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
        
        # Crear lista completa de 24 horas
        hourly_distribution = []
        for hour in range(24):
            hourly_distribution.append({
                'hora': f"{hour:02d}:00",
                'acciones': hourly_counts.get(hour, 0)
            })
        
        return hourly_distribution
    
    @staticmethod
    def _get_user_daily_activity(user_id: int, days: int) -> List[Dict[str, Any]]:
        """
        Obtener actividad diaria de un usuario específico.
        
        Args:
            user_id: ID del usuario
            days: Número de días hacia atrás
            
        Returns:
            Lista con actividad por día
        """
        time_threshold = timezone.now() - timedelta(days=days)
        
        user_logs = Bitacora.objects.filter(
            usuario_id=user_id,
            fecha__gte=time_threshold
        )
        
        daily_activity = {}
        for log in user_logs:
            day_key = log.fecha.strftime('%Y-%m-%d')
            daily_activity[day_key] = daily_activity.get(day_key, 0) + 1
        
        # Crear lista ordenada
        activity_list = []
        for day, count in sorted(daily_activity.items()):
            activity_list.append({
                'fecha': day,
                'acciones': count
            })
        
        return activity_list
