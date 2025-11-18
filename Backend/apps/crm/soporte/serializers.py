# apps/crm/soporte/serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Ticket, MensajeTicket
from apps.ecommerce.pedidos.models import Pedido
from apps.crm.crm_preventa.serializers import UsuarioSimpleSerializer

User = get_user_model()

# --- Serializadores de LECTURA (Para mostrar la conversación) ---
class MensajeTicketSerializer(serializers.ModelSerializer):
    """
    Serializador para mostrar un mensaje individual dentro de un ticket.
    """
    usuario = UsuarioSimpleSerializer(read_only=True)
    adjunto_url = serializers.SerializerMethodField()

    class Meta:
        model = MensajeTicket
        fields = ('id', 'usuario', 'mensaje', 'adjunto', 'adjunto_url', 'creado_en')
        read_only_fields = ('id', 'usuario', 'mensaje', 'adjunto_url', 'creado_en')

    def get_adjunto_url(self, obj):
        if obj.adjunto and hasattr(obj.adjunto, 'url'):
            return obj.adjunto.url
        return None

class TicketSerializer(serializers.ModelSerializer):
    """
    Serializador de LECTURA COMPLETA de un Ticket.
    Muestra el ticket y anida todos sus mensajes.
    """
    cliente = UsuarioSimpleSerializer(read_only=True)
    agente_asignado = UsuarioSimpleSerializer(read_only=True)
    
    # Anidamos la conversación completa
    mensajes = MensajeTicketSerializer(many=True, read_only=True)
    
    # Mostramos los valores legibles
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)

    class Meta:
        model = Ticket
        fields = (
            'id', 'cliente', 'agente_asignado', 'pedido', 
            'asunto', 'estado', 'estado_display', 
            'prioridad', 'prioridad_display',
            'creado_en', 'actualizado_en',
            'mensajes' # La lista de mensajes
        )
        read_only_fields = fields

# --- Serializadores de ESCRITURA (Para crear y gestionar) ---
class TicketCreateSerializer(serializers.ModelSerializer):
    """
    Serializador para que el CLIENTE cree un nuevo ticket.
    Debe incluir el primer mensaje.
    """
    # Campo para el primer mensaje (no es parte del modelo Ticket)
    mensaje = serializers.CharField(write_only=True)
    adjunto = serializers.ImageField(required=False, write_only=True)

    # El cliente puede vincularlo a un pedido
    pedido_id = serializers.PrimaryKeyRelatedField(
        queryset=Pedido.objects.all(),
        source='pedido',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Ticket
        fields = ('asunto', 'pedido_id', 'prioridad', 'mensaje', 'adjunto')

    def validate_pedido_id(self, pedido):
        """
        Valida que el pedido pertenezca al usuario que crea el ticket.
        """
        usuario = self.context['request'].user
        if pedido and pedido.usuario != usuario:
            raise serializers.ValidationError("Este pedido no pertenece al usuario actual.")
        return pedido

    def create(self, validated_data):
        # Sacamos los datos que no son del modelo Ticket
        mensaje_texto = validated_data.pop('mensaje')
        adjunto_imagen = validated_data.pop('adjunto', None)
        
        # El cliente es el usuario que hace la petición
        cliente = self.context['request'].user
        
        # 1. Creamos el Ticket
        ticket = Ticket.objects.create(cliente=cliente, **validated_data)
        
        # 2. Creamos el primer Mensaje
        MensajeTicket.objects.create(
            ticket=ticket,
            usuario=cliente,
            mensaje=mensaje_texto,
            adjunto=adjunto_imagen
        )
        
        return ticket

class TicketUpdateSerializer(serializers.ModelSerializer):
    """
    Serializador para que el ADMIN actualice un ticket
    (reasignar, cambiar estado).
    """
    agente_asignado_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_staff=True),
        source='agente_asignado',
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Ticket
        fields = ('estado', 'prioridad', 'agente_asignado_id')


class MensajeCreateSerializer(serializers.ModelSerializer):
    """
    Serializador para que CLIENTE o ADMIN añadan un nuevo
    mensaje a un ticket EXISTENTE.
    """
    class Meta:
        model = MensajeTicket
        fields = ('mensaje', 'adjunto')
    
    def create(self, validated_data):
        # El usuario es quien hace la petición (cliente o admin)
        usuario = self.context['request'].user
        # El ticket se obtiene de la URL (lo pasamos desde la vista)
        ticket = self.context['ticket']

        # Validar que el usuario tenga permiso para responder
        if not (usuario.is_staff or ticket.cliente == usuario):
             raise serializers.ValidationError("No tienes permiso para responder a este ticket.")

        return MensajeTicket.objects.create(
            ticket=ticket, 
            usuario=usuario, 
            **validated_data
        )