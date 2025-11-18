# apps/crm/clientes/views.py
from rest_framework import generics, viewsets, permissions
from .models import Cliente, Segmento
from .serializers import ClienteSerializer, SegmentoSerializer

# --- Vista para el Cliente (Mi Perfil 360) ---
class MiPerfilClienteView(generics.RetrieveAPIView):
    """
    (CLIENTE) Vista de solo lectura para que un cliente
    vea su propio "Perfil 360" (cuánto ha gastado, etc.)
    
    Endpoint: GET /api/clientes/mi-perfil/
    """
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Sobrescribe para devolver siempre el perfil del usuario logueado.
        El signal 'crear_perfil_cliente' asegura que siempre exista.
        """
        return Cliente.objects.get(usuario=self.request.user)

# --- Vistas de ADMINISTRACIÓN ---
class AdminSegmentoViewSet(viewsets.ModelViewSet):
    """
    (ADMIN) CRUD completo para gestionar los Segmentos de clientes
    (Ej: "VIP", "En Riesgo").
    """
    queryset = Segmento.objects.all()
    serializer_class = SegmentoSerializer
    permission_classes = [permissions.IsAdminUser] # Solo staff/admin

class AdminClienteViewSet(viewsets.ModelViewSet):
    """
    (ADMIN) CRUD completo para gestionar todos los Perfiles 360.
    Permite al admin ver las estadísticas y asignar
    manualmente estados o segmentos.
    """
    queryset = Cliente.objects.all().select_related('usuario').prefetch_related('segmentos')
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAdminUser]
    
    # ¡Filtros para segmentación!
    filterset_fields = {
        'estado': ['exact'],
        'segmentos': ['exact'],
        'total_gastado': ['gte', 'lte'], # gte = mayor o igual, lte = menor o igual
        'total_pedidos': ['gte', 'lte'],
        'fecha_ultima_compra': ['gte', 'lte']
    }
    search_fields = ['usuario__email', 'usuario__first_name', 'usuario__last_name']