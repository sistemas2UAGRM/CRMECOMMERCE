import 'package:dio/dio.dart';
import '../api_client.dart';
import '../models/direccion.dart';

// SWAGGER-CORRECTED: Servicio para gestión de direcciones del usuario
class AddressService {
  final ApiClient _apiClient = ApiClient();

  /// Obtener todas las direcciones del usuario autenticado
  /// SWAGGER-CORRECTED: GET /users/direcciones/
  /// Soporta paginación DRF: { count, next, results }
  Future<List<Direccion>> getAddresses() async {
    try {
      final response = await _apiClient.get('/users/direcciones/');

      if (response.statusCode == 200) {
        final data = response.data;

        // Manejar paginación DRF
        List<dynamic> direccionesJson;
        if (data is Map && data['results'] != null) {
          direccionesJson = data['results'] as List;
        } else if (data is List) {
          direccionesJson = data;
        } else {
          throw Exception('Formato de respuesta inesperado');
        }

        return direccionesJson.map((json) => Direccion.fromJson(json)).toList();
      } else {
        throw Exception('Error al obtener direcciones: ${response.statusCode}');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw Exception('No autorizado. Inicia sesión nuevamente');
      } else if (e.type == DioExceptionType.connectionError) {
        throw Exception('No se puede conectar al servidor');
      }
      rethrow;
    } catch (e) {
      throw Exception('Error al obtener direcciones: $e');
    }
  }

  /// Agregar una nueva dirección
  /// SWAGGER-CORRECTED: POST /users/direcciones/
  Future<Direccion> addAddress(Direccion direccion) async {
    try {
      final response = await _apiClient.post(
        '/users/direcciones/',
        data: direccion.toJson(),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        return Direccion.fromJson(response.data);
      } else {
        throw Exception('Error al agregar dirección: ${response.statusCode}');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw Exception('No autorizado. Inicia sesión nuevamente');
      } else if (e.response?.statusCode == 400) {
        final message =
            e.response?.data['detail'] ?? 'Datos de dirección inválidos';
        throw Exception(message);
      } else if (e.type == DioExceptionType.connectionError) {
        throw Exception('No se puede conectar al servidor');
      }
      rethrow;
    } catch (e) {
      throw Exception('Error al agregar dirección: $e');
    }
  }

  /// Actualizar una dirección existente
  /// SWAGGER-CORRECTED: PUT /users/direcciones/{id}/
  Future<Direccion> updateAddress(int id, Direccion direccion) async {
    try {
      final response = await _apiClient.dio.put(
        '/users/direcciones/$id/',
        data: direccion.toJson(),
      );

      if (response.statusCode == 200) {
        return Direccion.fromJson(response.data);
      } else {
        throw Exception(
            'Error al actualizar dirección: ${response.statusCode}');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw Exception('No autorizado. Inicia sesión nuevamente');
      } else if (e.response?.statusCode == 404) {
        throw Exception('Dirección no encontrada');
      } else if (e.type == DioExceptionType.connectionError) {
        throw Exception('No se puede conectar al servidor');
      }
      rethrow;
    } catch (e) {
      throw Exception('Error al actualizar dirección: $e');
    }
  }

  /// Eliminar una dirección
  /// SWAGGER-CORRECTED: DELETE /users/direcciones/{id}/
  Future<void> deleteAddress(int id) async {
    try {
      final response = await _apiClient.delete('/users/direcciones/$id/');

      if (response.statusCode != 200 && response.statusCode != 204) {
        throw Exception('Error al eliminar dirección: ${response.statusCode}');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw Exception('No autorizado. Inicia sesión nuevamente');
      } else if (e.response?.statusCode == 404) {
        throw Exception('Dirección no encontrada');
      } else if (e.type == DioExceptionType.connectionError) {
        throw Exception('No se puede conectar al servidor');
      }
      rethrow;
    } catch (e) {
      throw Exception('Error al eliminar dirección: $e');
    }
  }
}
