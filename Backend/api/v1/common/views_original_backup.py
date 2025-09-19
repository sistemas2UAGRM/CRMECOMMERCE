# api/v1/common/views.py

"""
📚 MICROCONCEPTOS - VIEWS PARA AUDITORÍA Y BITÁCORA

Los sistemas de auditoría requieren consideraciones especiales:

1. SOLO LECTURA: La bitácora no debe ser modificable via API
2. FILTRADO EFICIENTE: Grandes volúmenes de datos requieren filtros optimizados
3. PAGINACIÓN: Esencial para performance con muchos registros
4. PERMISOS GRANULARES: Solo ciertos roles pueden ver información sensible
5. AGREGACIONES: Estadísticas y reportes son comunes

Patrones implementados:
- ReadOnlyModelViewSet para proteger datos de auditoría
- Filtros personalizados para consultas complejas
- Optimizaciones de queries con select_related/prefetch_related
- Endpoints de estadísticas para dashboards
"""

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta, datetime
from django.core.paginator import Paginator

from core.common.models import Bitacora
from core.users.models import User
from .serializers import (
    BitacoraListSerializer, BitacoraDetailSerializer, BitacoraCreateSerializer,
    BitacoraStatsSerializer, BitacoraFilterSerializer
)


class BitacoraViewSet(viewsets.ReadOnlyModelViewSet):
    """
    📝 MICROCONCEPTO: ReadOnlyModelViewSet para auditoría
    
    La bitácora es un registro de auditoría que NO debe ser modificable
    via API. Solo permite operaciones de lectura:
    - list(): GET /common/bitacora/ (listar registros)
    - retrieve(): GET /common/bitacora/{id}/ (detalle de registro)
    
    Incluye filtros avanzados y optimizaciones para grandes volúmenes.
    """
    
    queryset = Bitacora.objects.select_related('usuario').order_by('-fecha')
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['fecha', 'accion', 'usuario__username']
    ordering = ['-fecha']  # Por defecto, más recientes primero
    
    def get_serializer_class(self):
        """
        📝 MICROCONCEPTO: Serializers optimizados por uso
        
        - list: Serializer ligero para performance
        - retrieve: Serializer completo con detalles
        """
        if self.action == 'list':
            return BitacoraListSerializer
        return BitacoraDetailSerializer
    
    def get_permissions(self):
        """
        📝 MICROCONCEPTO: Permisos basados en jerarquía
        
        - Administradores: Acceso completo
        - Supervisores: Solo su equipo
        - Vendedores: Solo sus propias acciones
        - Clientes: Sin acceso
        """
        user = self.request.user
        if user.is_authenticated:
            user_groups = user.groups.values_list('name', flat=True)
            
            if 'administrador' in user_groups:
                return [permissions.IsAuthenticated()]
            elif 'empleadonivel1' in user_groups:  # Supervisor
                return [permissions.IsAuthenticated()]
            elif 'empleadonivel2' in user_groups:  # Vendedor
                return [permissions.IsAuthenticated()]
            else:  # Cliente
                return [permissions.IsAdminUser()]  # Deniega acceso
        
        return [permissions.IsAdminUser()]
    
    def get_queryset(self):
        """
        📝 MICROCONCEPTO: Filtrado de queryset por permisos
        
        Cada rol ve diferentes niveles de información:
        - Administrador: Todo
        - Supervisor: Su equipo + sus acciones
        - Vendedor: Solo sus acciones
        """
        user = self.request.user
        queryset = super().get_queryset()
        
        if not user.is_authenticated:
            return queryset.none()
        
        user_groups = user.groups.values_list('name', flat=True)
        
        if 'administrador' in user_groups:
            # Administradores ven todo
            return queryset
        elif 'empleadonivel1' in user_groups:
            # Supervisores ven su equipo (vendedores) + sus propias acciones
            vendedores = User.objects.filter(groups__name='empleadonivel2')
            return queryset.filter(
                Q(usuario=user) | Q(usuario__in=vendedores)
            )
        elif 'empleadonivel2' in user_groups:
            # Vendedores solo ven sus propias acciones
            return queryset.filter(usuario=user)
        else:
            # Otros roles no tienen acceso
            return queryset.none()
    
    def list(self, request):
        """
        📝 MICROCONCEPTO: List personalizado con filtros
        
        Agregamos filtros personalizados y estadísticas básicas.
        """
        # Aplicar filtros personalizados
        queryset = self.apply_custom_filters(request)
        
        # Paginación
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        # Sin paginación (no recomendado para bitácora)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
    
    def apply_custom_filters(self, request):
        """
        📝 MICROCONCEPTO: Filtros personalizados
        
        Implementamos filtros que no están disponibles en DRF por defecto.
        """
        queryset = self.get_queryset()
        
        # Filtro por rango de fechas
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        
        if fecha_inicio:
            try:
                fecha_inicio = datetime.fromisoformat(fecha_inicio.replace('Z', '+00:00'))
                queryset = queryset.filter(fecha__gte=fecha_inicio)
            except ValueError:
                pass  # Ignorar formato inválido
        
        if fecha_fin:
            try:
                fecha_fin = datetime.fromisoformat(fecha_fin.replace('Z', '+00:00'))
                queryset = queryset.filter(fecha__lte=fecha_fin)
            except ValueError:
                pass
        
        # Filtro por usuario
        usuario_id = request.query_params.get('usuario_id')
        if usuario_id:
            try:
                queryset = queryset.filter(usuario_id=int(usuario_id))
            except (ValueError, TypeError):
                pass
        
        # Filtro por acción (búsqueda parcial)
        accion = request.query_params.get('accion_contiene')
        if accion:
            queryset = queryset.filter(accion__icontains=accion)
        
        # Filtro por IP
        ip = request.query_params.get('ip')
        if ip:
            queryset = queryset.filter(ip=ip)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        📝 MICROCONCEPTO: Endpoint de estadísticas
        
        Proporciona métricas útiles para dashboards de administración.
        """
        # Solo administradores y supervisores pueden ver estadísticas
        user_groups = request.user.groups.values_list('name', flat=True)
        if not any(role in user_groups for role in ['administrador', 'empleadonivel1']):
            return Response(
                {'error': 'No tiene permisos para ver estadísticas'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = self.get_queryset()
        
        # Estadísticas básicas
        total_acciones = queryset.count()
        
        # Acciones de hoy
        hoy = timezone.now().date()
        acciones_hoy = queryset.filter(fecha__date=hoy).count()
        
        # Acciones de la última semana
        semana_pasada = timezone.now() - timedelta(days=7)
        acciones_ultima_semana = queryset.filter(fecha__gte=semana_pasada).count()
        
        # Usuarios activos hoy (que han realizado alguna acción)
        usuarios_activos_hoy = queryset.filter(
            fecha__date=hoy
        ).values('usuario').distinct().count()
        
        # Acciones por tipo (análisis de texto básico)
        acciones_por_tipo = {}
        tipos_comunes = ['Login', 'Registro', 'Actualización', 'Creación', 'Eliminación']
        
        for tipo in tipos_comunes:
            count = queryset.filter(accion__icontains=tipo.lower()).count()
            if count > 0:
                acciones_por_tipo[tipo] = count
        
        # IPs más frecuentes (top 5)
        ips_frecuentes = list(
            queryset.values('ip')
            .annotate(count=Count('ip'))
            .order_by('-count')[:5]
            .values_list('ip', 'count')
        )
        
        stats_data = {
            'total_acciones': total_acciones,
            'acciones_hoy': acciones_hoy,
            'acciones_ultima_semana': acciones_ultima_semana,
            'usuarios_activos_hoy': usuarios_activos_hoy,
            'acciones_por_tipo': acciones_por_tipo,
            'ips_mas_frecuentes': [{'ip': ip, 'count': count} for ip, count in ips_frecuentes]
        }
        
        serializer = BitacoraStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        📝 MICROCONCEPTO: Exportación de datos
        
        Endpoint para exportar datos de bitácora (implementación básica).
        En producción, esto debería ser un task asíncrono.
        """
        # Solo administradores pueden exportar
        if not request.user.groups.filter(name='administrador').exists():
            return Response(
                {'error': 'Solo administradores pueden exportar datos'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Aplicar filtros
        queryset = self.apply_custom_filters(request)
        
        # Limitar exportación para evitar problemas de memoria
        if queryset.count() > 10000:
            return Response(
                {'error': 'Demasiados registros para exportar. Use filtros para reducir el conjunto.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Serializar datos
        serializer = BitacoraListSerializer(queryset, many=True)
        
        return Response({
            'message': 'Datos preparados para exportación',
            'count': queryset.count(),
            'data': serializer.data
        })


class BitacoraCreateView(APIView):
    """
    📝 MICROCONCEPTO: Vista interna para crear registros
    
    Esta vista es para uso interno del sistema, no para usuarios finales.
    Permite que otros módulos registren acciones en la bitácora.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Crear un nuevo registro de bitácora
        """
        # Solo el sistema interno debería usar esto
        # En producción, esto podría requerir un token especial
        
        serializer = BitacoraCreateSerializer(data=request.data)
        if serializer.is_valid():
            bitacora = serializer.save()
            response_serializer = BitacoraDetailSerializer(bitacora)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BitacoraFilterView(APIView):
    """
    📝 MICROCONCEPTO: Vista para validar filtros
    
    Endpoint para validar filtros antes de aplicarlos,
    útil para UIs complejas de filtrado.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Validar filtros de bitácora
        """
        serializer = BitacoraFilterSerializer(data=request.data)
        if serializer.is_valid():
            return Response({
                'valid': True,
                'message': 'Filtros válidos',
                'filters': serializer.validated_data
            })
        
        return Response({
            'valid': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
