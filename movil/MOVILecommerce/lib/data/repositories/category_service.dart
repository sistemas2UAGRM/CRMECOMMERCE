import 'package:dio/dio.dart';
import '../api_client.dart';
import '../models/categoria.dart';

// SWAGGER-CORRECTED: Servicio para categorías de productos
class CategoryService {
  final ApiClient _apiClient = ApiClient();

  /// Obtener todas las categorías
  /// SWAGGER-CORRECTED: GET /ecommerce/categorias/
  Future<List<Categoria>> getCategories() async {
    try {
      final response = await _apiClient.get('/ecommerce/categorias/');

      if (response.statusCode == 200) {
        final data = response.data;

        // Manejar posible paginación o lista directa
        List<dynamic> categoriasJson;
        if (data is Map && data['results'] != null) {
          categoriasJson = data['results'] as List;
        } else if (data is List) {
          categoriasJson = data;
        } else {
          throw Exception('Formato de respuesta inesperado');
        }

        return categoriasJson.map((json) => Categoria.fromJson(json)).toList();
      } else {
        throw Exception('Error al obtener categorías: ${response.statusCode}');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return [];
      } else if (e.type == DioExceptionType.connectionError) {
        throw Exception('No se puede conectar al servidor');
      }
      rethrow;
    } catch (e) {
      throw Exception('Error al obtener categorías: $e');
    }
  }
}
