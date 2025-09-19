# api/v1/common/mixins/audit_mixin.py

"""
📚 MIXIN PARA AUDITORÍA AUTOMÁTICA

Este mixin proporciona funcionalidad de auditoría reutilizable
para cualquier ViewSet que necesite registrar acciones en bitácora.

Beneficios:
- Código reutilizable
- Auditoría consistente
- Fácil de mantener
- Configurable por view
"""

from core.common.models import Bitacora


class AuditMixin:
    """
    Mixin que agrega auditoría automática a ViewSets.
    
    Uso:
        class MiViewSet(AuditMixin, viewsets.ModelViewSet):
            audit_action_prefix = "Usuario"  # Opcional
    """
    
    audit_action_prefix = ""  # Prefijo para las acciones de auditoría
    audit_enabled = True      # Habilitar/deshabilitar auditoría
    
    def perform_create(self, serializer):
        """Auditoría automática en creación"""
        instance = serializer.save()
        if self.audit_enabled:
            action = f"{self.audit_action_prefix} creado: {instance}"
            self.log_audit_action(action, instance)
        return instance
    
    def perform_update(self, serializer):
        """Auditoría automática en actualización"""
        instance = serializer.save()
        if self.audit_enabled:
            action = f"{self.audit_action_prefix} actualizado: {instance}"
            self.log_audit_action(action, instance)
        return instance
    
    def perform_destroy(self, instance):
        """Auditoría automática en eliminación"""
        if self.audit_enabled:
            action = f"{self.audit_action_prefix} eliminado: {instance}"
            self.log_audit_action(action, instance)
        super().perform_destroy(instance)
    
    def log_audit_action(self, action, instance=None):
        """
        Registrar acción en bitácora
        
        Args:
            action (str): Descripción de la acción
            instance: Instancia relacionada (opcional)
        """
        try:
            Bitacora.objects.create(
                accion=action,
                ip=self.get_client_ip(),
                usuario=self.request.user if self.request.user.is_authenticated else None
            )
        except Exception as e:
            # Log error pero no fallar la operación principal
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error en auditoría: {e}")
    
    def get_client_ip(self):
        """Obtener IP del cliente"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip or '127.0.0.1'
