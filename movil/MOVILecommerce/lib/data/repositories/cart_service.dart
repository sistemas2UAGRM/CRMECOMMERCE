import 'package:dio/dio.dart';
import '../api_client.dart';
import '../models/carrito_response.dart';

// SWAGGER-CORRECTED: Servicio de carrito 100% server-side
class CartService {
  final ApiClient _apiClient = ApiClient();

  /// Obtener el carrito del usuario autenticado
  /// SWAGGER-CORRECTED: GET /ecommerce/carrito/
  /// Retorna un objeto con { id, usuario, subtotal, total_items, items[] }
  Future<CarritoResponse> getCart() async {
    try {
      final response = await _apiClient.get('/ecommerce/carrito/');

      if (response.statusCode == 200) {
        final data = response.data;

        // El endpoint devuelve un objeto, no una lista
        if (data is Map<String, dynamic>) {
          return CarritoResponse.fromJson(data);
        } else {
          throw Exception('Formato de respuesta inesperado');
        }
      } else {
        throw Exception('Error al obtener carrito: ${response.statusCode}');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw Exception('No autorizado. Inicia sesión para ver tu carrito');
      } else if (e.type == DioExceptionType.connectionError) {
        throw Exception('No se puede conectar al servidor');
      }
      rethrow;
    } catch (e) {
      throw Exception('Error al obtener carrito: $e');
    }
  }

  /// Añadir un producto al carrito
  /// SWAGGER-CORRECTED: POST /ecommerce/carrito/agregar_item/
  /// Body: { "producto_id": 1, "cantidad": 2 }
  /// Retorna el carrito completo actualizado { id, usuario, subtotal, total_items, items[] }
  Future<CarritoResponse> addToCart(int productId, int quantity) async {
    try {
      final response = await _apiClient.post(
        '/ecommerce/carrito/agregar_item/',
        data: {
          'producto_id': productId,
          'cantidad': quantity,
        },
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        final data = response.data;

        // El backend retorna el carrito completo como objeto
        if (data is Map<String, dynamic>) {
          return CarritoResponse.fromJson(data);
        } else {
          throw Exception('Formato de respuesta inesperado');
        }
      } else {
        throw Exception('Error al añadir al carrito: ${response.statusCode}');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw Exception(
            'Debes iniciar sesión para agregar productos al carrito');
      } else if (e.response?.statusCode == 400) {
        final message =
            e.response?.data['detail'] ?? 'Producto no válido o sin stock';
        throw Exception(message);
      } else if (e.type == DioExceptionType.connectionError) {
        throw Exception('No se puede conectar al servidor');
      }
      rethrow;
    } catch (e) {
      throw Exception('Error al añadir al carrito: $e');
    }
  }

  /// Eliminar un item del carrito
  /// SWAGGER-CORRECTED: DELETE /ecommerce/carrito/items/{itemId}/eliminar/
  Future<void> removeFromCart(int itemId) async {
    try {
      final response = await _apiClient.delete(
        '/ecommerce/carrito/items/$itemId/eliminar/',
      );

      if (response.statusCode != 200 && response.statusCode != 204) {
        throw Exception('Error al eliminar item: ${response.statusCode}');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw Exception('No autorizado');
      } else if (e.response?.statusCode == 404) {
        throw Exception('Item no encontrado');
      } else if (e.type == DioExceptionType.connectionError) {
        throw Exception('No se puede conectar al servidor');
      }
      rethrow;
    } catch (e) {
      throw Exception('Error al eliminar item: $e');
    }
  }

  /// Crear pedido desde el carrito (checkout)
  /// SWAGGER-CORRECTED: POST /ecommerce/carrito/crear_pedido/
  /// Sin body, retorna el Pedido creado con su ID
  Future<int> checkout() async {
    try {
      final response =
          await _apiClient.post('/ecommerce/carrito/crear_pedido/');

      if (response.statusCode == 200 || response.statusCode == 201) {
        final pedidoId = response.data['id'];
        return pedidoId as int;
      } else {
        throw Exception('Error al crear pedido: ${response.statusCode}');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw Exception('No autorizado');
      } else if (e.response?.statusCode == 400) {
        final message =
            e.response?.data['detail'] ?? 'Carrito vacío o sin dirección';
        throw Exception(message);
      } else if (e.type == DioExceptionType.connectionError) {
        throw Exception('No se puede conectar al servidor');
      }
      rethrow;
    } catch (e) {
      throw Exception('Error al crear pedido: $e');
    }
  }
}
