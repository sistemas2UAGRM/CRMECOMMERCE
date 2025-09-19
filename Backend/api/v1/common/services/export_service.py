# api/v1/common/services/export_service.py

"""
🔄 SERVICIO DE EXPORTACIÓN - GESTIÓN DE DATOS

Este servicio centraliza todas las funcionalidades de exportación:
- Validaciones de permisos para exportación
- Formateo de datos para diferentes formatos
- Manejo de grandes volúmenes de datos
- Preparación para exportación asíncrona

Casos de uso implementados:
- CU-CM07: Exportación de datos de bitácora
- CU-CM08: Validación de límites de exportación
- CU-CM09: Formateo para múltiples formatos
"""

from django.utils import timezone
from django.contrib.auth import get_user_model
from typing import Dict, List, Any, Optional
import csv
import json
from io import StringIO

from core.common.models import Bitacora

User = get_user_model()


class ExportService:
    """
    Servicio centralizado para funcionalidades de exportación
    """
    
    # Límites de exportación
    MAX_EXPORT_RECORDS = 10000
    SUPPORTED_FORMATS = ['json', 'csv', 'txt']
    
    @staticmethod
    def validate_export_permissions(user) -> Dict[str, Any]:
        """
        CU-CM08: Validar permisos de exportación del usuario.
        
        Args:
            user: Usuario solicitante
            
        Returns:
            Diccionario con resultado de validación
        """
        # Solo administradores pueden exportar datos de bitácora
        if not user.groups.filter(name='administrador').exists():
            return {
                'valid': False,
                'error': 'Solo administradores pueden exportar datos de bitácora',
                'required_role': 'administrador',
                'user_roles': list(user.groups.values_list('name', flat=True))
            }
        
        return {
            'valid': True,
            'message': 'Usuario autorizado para exportar datos'
        }
    
    @staticmethod
    def validate_export_size(queryset_count: int) -> Dict[str, Any]:
        """
        CU-CM08: Validar tamaño del conjunto de datos a exportar.
        
        Args:
            queryset_count: Cantidad de registros a exportar
            
        Returns:
            Diccionario con resultado de validación
        """
        if queryset_count == 0:
            return {
                'valid': False,
                'error': 'No hay registros que coincidan con los filtros especificados',
                'count': 0
            }
        
        if queryset_count > ExportService.MAX_EXPORT_RECORDS:
            return {
                'valid': False,
                'error': f'Demasiados registros para exportar ({queryset_count:,}). '
                        f'El límite es {ExportService.MAX_EXPORT_RECORDS:,}. '
                        f'Use filtros para reducir el conjunto.',
                'count': queryset_count,
                'limit': ExportService.MAX_EXPORT_RECORDS,
                'excess': queryset_count - ExportService.MAX_EXPORT_RECORDS
            }
        
        return {
            'valid': True,
            'count': queryset_count,
            'message': f'Tamaño de exportación válido: {queryset_count:,} registros'
        }
    
    @staticmethod
    def prepare_export_data(queryset, include_sensitive: bool = False) -> List[Dict[str, Any]]:
        """
        CU-CM07: Preparar datos de bitácora para exportación.
        
        Args:
            queryset: QuerySet de Bitacora a exportar
            include_sensitive: Incluir datos sensibles (IP, detalles completos)
            
        Returns:
            Lista de diccionarios con datos formateados
        """
        export_data = []
        
        for registro in queryset.select_related('usuario'):
            # Datos básicos siempre incluidos
            record_data = {
                'id': getattr(registro, 'id', ''),
                'fecha': registro.fecha.isoformat() if registro.fecha else '',
                'usuario': registro.usuario.username if registro.usuario else '',
                'accion': registro.accion or '',
                'objeto_tipo': getattr(registro, 'objeto_tipo', ''),
                'objeto_id': getattr(registro, 'objeto_id', '')
            }
            
            # Datos sensibles solo si se solicitan y hay permisos
            if include_sensitive:
                record_data.update({
                    'ip': getattr(registro, 'ip', ''),
                    'detalles': getattr(registro, 'detalles', '')
                })
            else:
                # Versión resumida de detalles
                detalles = getattr(registro, 'detalles', '')
                if detalles and len(detalles) > 100:
                    record_data['detalles_resumen'] = detalles[:100] + '...'
                else:
                    record_data['detalles_resumen'] = detalles
            
            # Información del usuario (no sensible)
            if registro.usuario:
                record_data['usuario_info'] = {
                    'username': registro.usuario.username,
                    'nombre_completo': f"{registro.usuario.first_name} {registro.usuario.last_name}".strip(),
                    'grupos': list(registro.usuario.groups.values_list('name', flat=True))
                }
            
            export_data.append(record_data)
        
        return export_data
    
    @staticmethod
    def format_as_json(data: List[Dict[str, Any]], pretty: bool = True) -> str:
        """
        CU-CM09: Formatear datos como JSON.
        
        Args:
            data: Lista de diccionarios con datos
            pretty: Si usar formato legible
            
        Returns:
            String con datos en formato JSON
        """
        if pretty:
            return json.dumps(data, indent=2, ensure_ascii=False, default=str)
        else:
            return json.dumps(data, ensure_ascii=False, default=str)
    
    @staticmethod
    def format_as_csv(data: List[Dict[str, Any]]) -> str:
        """
        CU-CM09: Formatear datos como CSV.
        
        Args:
            data: Lista de diccionarios con datos
            
        Returns:
            String con datos en formato CSV
        """
        if not data:
            return ""
        
        # Obtener todas las claves posibles (campos)
        all_keys = set()
        for record in data:
            all_keys.update(record.keys())
            # También incluir claves de objetos anidados
            for key, value in record.items():
                if isinstance(value, dict):
                    for nested_key in value.keys():
                        all_keys.add(f"{key}.{nested_key}")
        
        # Ordenar campos para consistencia
        fieldnames = sorted(all_keys)
        
        # Crear CSV
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        
        # Aplanar datos anidados para CSV
        for record in data:
            flattened_record = ExportService._flatten_dict(record)
            writer.writerow(flattened_record)
        
        return output.getvalue()
    
    @staticmethod
    def format_as_txt(data: List[Dict[str, Any]]) -> str:
        """
        CU-CM09: Formatear datos como texto plano.
        
        Args:
            data: Lista de diccionarios con datos
            
        Returns:
            String con datos en formato texto
        """
        if not data:
            return "No hay datos para exportar."
        
        lines = []
        lines.append("=" * 80)
        lines.append("EXPORTACIÓN DE BITÁCORA")
        lines.append(f"Fecha de exportación: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Total de registros: {len(data)}")
        lines.append("=" * 80)
        lines.append("")
        
        for i, record in enumerate(data, 1):
            lines.append(f"REGISTRO #{i}")
            lines.append("-" * 40)
            
            # Campos principales
            lines.append(f"ID: {record.get('id', 'N/A')}")
            lines.append(f"Fecha: {record.get('fecha', 'N/A')}")
            lines.append(f"Usuario: {record.get('usuario', 'N/A')}")
            lines.append(f"Acción: {record.get('accion', 'N/A')}")
            
            # Información adicional si existe
            if record.get('objeto_tipo'):
                lines.append(f"Objeto: {record.get('objeto_tipo')} #{record.get('objeto_id', 'N/A')}")
            
            if record.get('detalles_resumen'):
                lines.append(f"Detalles: {record.get('detalles_resumen')}")
            
            if record.get('ip'):
                lines.append(f"IP: {record.get('ip')}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_export_metadata(
        user, 
        queryset_count: int, 
        filters_applied: Dict[str, Any],
        export_format: str
    ) -> Dict[str, Any]:
        """
        Generar metadatos de la exportación para auditoría.
        
        Args:
            user: Usuario que realiza la exportación
            queryset_count: Cantidad de registros exportados
            filters_applied: Filtros aplicados en la consulta
            export_format: Formato de exportación usado
            
        Returns:
            Diccionario con metadatos
        """
        return {
            'exportacion': {
                'fecha': timezone.now().isoformat(),
                'usuario': {
                    'id': user.id,
                    'username': user.username,
                    'nombre_completo': f"{user.first_name} {user.last_name}".strip()
                },
                'formato': export_format,
                'total_registros': queryset_count
            },
            'filtros_aplicados': filters_applied,
            'sistema': {
                'limite_maximo': ExportService.MAX_EXPORT_RECORDS,
                'formatos_soportados': ExportService.SUPPORTED_FORMATS
            }
        }
    
    @staticmethod
    def create_export_summary(
        export_data: List[Dict[str, Any]], 
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Crear resumen de la exportación realizada.
        
        Args:
            export_data: Datos exportados
            metadata: Metadatos de la exportación
            
        Returns:
            Diccionario con resumen
        """
        if not export_data:
            return {
                'resumen': 'No hay datos para exportar',
                'total_registros': 0
            }
        
        # Analizar datos exportados
        usuarios_unicos = set()
        acciones_tipos = {}
        rango_fechas = {'inicio': None, 'fin': None}
        
        for record in export_data:
            # Usuarios únicos
            if record.get('usuario'):
                usuarios_unicos.add(record['usuario'])
            
            # Tipos de acciones
            accion = record.get('accion', 'Sin especificar')
            acciones_tipos[accion] = acciones_tipos.get(accion, 0) + 1
            
            # Rango de fechas
            fecha_str = record.get('fecha')
            if fecha_str:
                try:
                    fecha = timezone.datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
                    if rango_fechas['inicio'] is None or fecha < rango_fechas['inicio']:
                        rango_fechas['inicio'] = fecha
                    if rango_fechas['fin'] is None or fecha > rango_fechas['fin']:
                        rango_fechas['fin'] = fecha
                except:
                    pass
        
        return {
            'resumen': {
                'total_registros': len(export_data),
                'usuarios_unicos': len(usuarios_unicos),
                'tipos_de_acciones': len(acciones_tipos),
                'periodo': {
                    'inicio': rango_fechas['inicio'].isoformat() if rango_fechas['inicio'] else None,
                    'fin': rango_fechas['fin'].isoformat() if rango_fechas['fin'] else None
                }
            },
            'distribucion_acciones': dict(sorted(acciones_tipos.items(), key=lambda x: x[1], reverse=True)[:10]),
            'usuarios_con_actividad': sorted(list(usuarios_unicos)),
            'metadatos': metadata
        }
    
    @staticmethod
    def _flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """
        Aplanar un diccionario anidado para CSV.
        
        Args:
            d: Diccionario a aplanar
            parent_key: Clave padre para recursión
            sep: Separador para claves anidadas
            
        Returns:
            Diccionario aplanado
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(ExportService._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Convertir listas a strings
                items.append((new_key, ', '.join(map(str, v))))
            else:
                items.append((new_key, v))
        return dict(items)
