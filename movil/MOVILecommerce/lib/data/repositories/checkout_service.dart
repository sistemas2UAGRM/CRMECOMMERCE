import '../api_client.dart';

class CheckoutService {
  final ApiClient _apiClient = ApiClient();

  /// Crear pedido desde el carrito actual
  /// POST /api/ecommerce/carrito/crear_pedido/
  Future<Map<String, dynamic>> crearPedido({
    required String metodoPago,
    required String direccionEnvio,
    String? comentario,
  }) async {
    try {
      final response = await _apiClient.post(
        '/ecommerce/carrito/crear_pedido/',
        data: {
          'metodo_pago': metodoPago, // "tarjeta", "efectivo", etc.
          'direccion_envio': direccionEnvio,
          if (comentario != null && comentario.isNotEmpty)
            'comentario': comentario,
        },
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        return response.data;
      } else {
        throw Exception(response.data['message'] ?? 'Error al crear el pedido');
      }
    } catch (e) {
      throw Exception('Error al crear el pedido: $e');
    }
  }

  /// Crear Payment Intent en Stripe
  /// POST /api/ecommerce/pagos/crear-payment-intent/
  Future<Map<String, dynamic>> crearPaymentIntent({
    required int pedidoId,
  }) async {
    try {
      final response = await _apiClient.post(
        '/ecommerce/pagos/crear-payment-intent/',
        data: {
          'pedido_id': pedidoId,
        },
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        return response.data;
      } else {
        throw Exception(
            response.data['message'] ?? 'Error al crear el payment intent');
      }
    } catch (e) {
      throw Exception('Error al crear el payment intent: $e');
    }
  }

  /// Verificar estado del pago
  /// POST /api/ecommerce/pagos/verificar-estado-pago/
  Future<Map<String, dynamic>> verificarEstadoPago({
    required String paymentIntentId,
  }) async {
    try {
      final response = await _apiClient.post(
        '/ecommerce/pagos/verificar-estado-pago/',
        data: {
          'payment_intent_id': paymentIntentId,
        },
      );

      if (response.statusCode == 200) {
        return response.data;
      } else {
        throw Exception(response.data['message'] ??
            'Error al verificar el estado del pago');
      }
    } catch (e) {
      throw Exception('Error al verificar el estado del pago: $e');
    }
  }
}
