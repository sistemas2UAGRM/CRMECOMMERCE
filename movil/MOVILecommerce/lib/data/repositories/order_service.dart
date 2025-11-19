import 'package:dio/dio.dart';
import '../api_client.dart';
import '../models/pedido.dart';

// SWAGGER-CORRECTED: Servicio de pedidos con endpoints reales
class OrderService {
  final ApiClient _apiClient = ApiClient();

  /// Obtener historial de pedidos del usuario autenticado
  /// SWAGGER-CORRECTED: GET /ecommerce/pedidos/
  /// Soporta paginación DRF
  Future<List<Pedido>> getOrderHistory() async {
    try {
      final response = await _apiClient.get('/ecommerce/pedidos/');

      if (response.statusCode == 200) {
        final data = response.data;

        // Manejar paginación DRF
        List<dynamic> pedidosJson;
        if (data is Map && data['results'] != null) {
          pedidosJson = data['results'] as List;
        } else if (data is List) {
          pedidosJson = data;
        } else {
          throw Exception('Formato de respuesta inesperado');
        }

        return pedidosJson.map((json) => Pedido.fromJson(json)).toList();
      } else {
        throw Exception('Error al obtener historial: ${response.statusCode}');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw Exception('No autorizado. Inicia sesión nuevamente');
      } else if (e.type == DioExceptionType.connectionError) {
        throw Exception('No se puede conectar al servidor');
      }
      rethrow;
    } catch (e) {
      throw Exception('Error al obtener historial de pedidos: $e');
    }
  }

  /// Obtener detalles de un pedido específico
  /// SWAGGER-CORRECTED: GET /ecommerce/pedidos/{id}/
  Future<Pedido> getOrderById(int orderId) async {
    try {
      final response = await _apiClient.get('/ecommerce/pedidos/$orderId/');

      if (response.statusCode == 200) {
        return Pedido.fromJson(response.data);
      } else {
        throw Exception('Error al obtener pedido: ${response.statusCode}');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw Exception('No autorizado');
      } else if (e.response?.statusCode == 404) {
        throw Exception('Pedido no encontrado');
      } else if (e.type == DioExceptionType.connectionError) {
        throw Exception('No se puede conectar al servidor');
      }
      rethrow;
    } catch (e) {
      throw Exception('Error al obtener detalles del pedido: $e');
    }
  }

  /// Iniciar pago de un pedido
  /// SWAGGER-CORRECTED: POST /ecommerce/pedidos/{id}/iniciar-pago/
  /// Retorna { "client_secret": "..." } para usar con Stripe
  Future<String> initiatePayment(int pedidoId) async {
    try {
      final response = await _apiClient.post(
        '/ecommerce/pedidos/$pedidoId/iniciar-pago/',
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        final clientSecret = response.data['client_secret'];
        if (clientSecret == null) {
          throw Exception('client_secret no encontrado en la respuesta');
        }
        return clientSecret as String;
      } else {
        throw Exception('Error al iniciar pago: ${response.statusCode}');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw Exception('No autorizado');
      } else if (e.response?.statusCode == 404) {
        throw Exception('Pedido no encontrado');
      } else if (e.response?.statusCode == 400) {
        final message =
            e.response?.data['detail'] ?? 'No se puede iniciar el pago';
        throw Exception(message);
      } else if (e.type == DioExceptionType.connectionError) {
        throw Exception('No se puede conectar al servidor');
      }
      rethrow;
    } catch (e) {
      throw Exception('Error al iniciar pago: $e');
    }
  }
}
