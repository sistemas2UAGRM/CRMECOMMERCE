# api/v1/common/mixins/ip_mixin.py

"""
📚 MIXIN PARA OBTENCIÓN DE IP

Mixin simple y reutilizable para obtener la IP del cliente
de manera consistente en todas las views.
"""


class IPMixin:
    """
    Mixin que proporciona funcionalidad para obtener la IP del cliente.
    
    Maneja correctamente:
    - Proxies y load balancers (X-Forwarded-For)
    - Conexiones directas (REMOTE_ADDR)
    - Casos edge con múltiples proxies
    """
    
    def get_client_ip(self):
        """
        Obtener IP del cliente de manera robusta.
        
        Returns:
            str: IP del cliente o '127.0.0.1' si no se puede determinar
        """
        # Verificar si existe request
        if not hasattr(self, 'request') or not self.request:
            return '127.0.0.1'
        
        # Obtener IP desde X-Forwarded-For (proxies/load balancers)
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Tomar la primera IP (cliente original)
            ip = x_forwarded_for.split(',')[0].strip()
            if ip:
                return ip
        
        # Obtener IP desde REMOTE_ADDR (conexión directa)
        remote_addr = self.request.META.get('REMOTE_ADDR')
        if remote_addr:
            return remote_addr.strip()
        
        # IP por defecto si no se puede determinar
        return '127.0.0.1'
    
    def get_all_client_ips(self):
        """
        Obtener todas las IPs en la cadena de proxies.
        
        Returns:
            list: Lista de IPs en orden (cliente -> proxies)
        """
        if not hasattr(self, 'request') or not self.request:
            return ['127.0.0.1']
        
        ips = []
        
        # IPs desde X-Forwarded-For
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            forwarded_ips = [ip.strip() for ip in x_forwarded_for.split(',')]
            ips.extend(forwarded_ips)
        
        # IP desde REMOTE_ADDR
        remote_addr = self.request.META.get('REMOTE_ADDR')
        if remote_addr and remote_addr.strip() not in ips:
            ips.append(remote_addr.strip())
        
        return ips if ips else ['127.0.0.1']
    
    def is_local_request(self):
        """
        Verificar si la request viene de localhost.
        
        Returns:
            bool: True si es request local
        """
        client_ip = self.get_client_ip()
        local_ips = ['127.0.0.1', '::1', 'localhost']
        return client_ip in local_ips
