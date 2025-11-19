import 'package:dio/dio.dart';
import '../api_client.dart';
import '../models/producto_list.dart';
import '../models/producto_detail.dart';

// SWAGGER-CORRECTED: Servicio de productos con endpoints reales
/// Servicio de productos que maneja el catálogo y detalles
class ProductService {
  final ApiClient _apiClient = ApiClient();

  /// Obtener lista de productos con búsqueda opcional
  /// SWAGGER-CORRECTED: GET /ecommerce/productos/?search={query}
  /// Soporta paginación DRF: { count, next, results }
  Future<Map<String, dynamic>> getProducts({
    String? search,
    int? page,
  }) async {
    try {
      // Construir parámetros de consulta
      final queryParameters = <String, dynamic>{};

      if (search != null && search.isNotEmpty) {
        queryParameters['search'] = search;
      }

      if (page != null) {
        queryParameters['page'] = page;
      }

      final response = await _apiClient.get(
        '/ecommerce/productos/',
        queryParameters: queryParameters.isNotEmpty ? queryParameters : null,
      );

      if (response.statusCode == 200) {
        final data = response.data;

        // Manejar paginación DRF
        if (data is Map && data['results'] != null) {
          final productos = (data['results'] as List)
              .map((json) => ProductoList.fromJson(json))
              .toList();

          return {
            'productos': productos,
            'count': data['count'],
            'next': data['next'],
            'previous': data['previous'],
          };
        } else if (data is List) {
          final productos =
              data.map((json) => ProductoList.fromJson(json)).toList();
          return {
            'productos': productos,
            'count': productos.length,
          };
        } else {
          throw Exception('Formato de respuesta no reconocido');
        }
      } else {
        throw DioException(
          requestOptions: response.requestOptions,
          response: response,
          type: DioExceptionType.badResponse,
          error: 'Error al obtener productos: ${response.statusCode}',
        );
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        // No hay productos, retornar lista vacía
        return {
          'productos': <ProductoList>[],
          'count': 0,
        };
      } else if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw Exception('Tiempo de espera agotado. Verifica tu conexión');
      } else if (e.type == DioExceptionType.connectionError) {
        throw Exception('No se puede conectar al servidor');
      }
      rethrow;
    } catch (e) {
      throw Exception('Error inesperado al obtener productos: $e');
    }
  }

  /// Obtener un producto por su ID
  /// SWAGGER-CORRECTED: GET /ecommerce/productos/{id}/
  Future<ProductoDetail> getProductById(int id) async {
    try {
      final response = await _apiClient.get('/ecommerce/productos/$id/');

      if (response.statusCode == 200) {
        return ProductoDetail.fromJson(response.data);
      } else {
        throw DioException(
          requestOptions: response.requestOptions,
          response: response,
          type: DioExceptionType.badResponse,
          error: 'Error al obtener producto: ${response.statusCode}',
        );
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        throw Exception('Producto no encontrado');
      } else if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw Exception('Tiempo de espera agotado. Verifica tu conexión');
      } else if (e.type == DioExceptionType.connectionError) {
        throw Exception('No se puede conectar al servidor');
      }
      rethrow;
    } catch (e) {
      throw Exception('Error al obtener producto: $e');
    }
  }
}
