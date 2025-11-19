import 'package:dio/dio.dart';
import '../api_client.dart';
import '../models/user_detail.dart';

// SWAGGER-CORRECTED: Servicio para gestión de perfil de usuario
class ProfileService {
  final ApiClient _apiClient = ApiClient();

  /// Obtener perfil del usuario autenticado
  /// SWAGGER-CORRECTED: GET /users/users/profile/
  Future<UserDetail> getProfile() async {
    try {
      final response = await _apiClient.get('/users/users/profile/');

      if (response.statusCode == 200) {
        return UserDetail.fromJson(response.data);
      } else {
        throw Exception('Error al obtener perfil: ${response.statusCode}');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw Exception('No autorizado. Inicia sesión nuevamente');
      } else if (e.type == DioExceptionType.connectionError) {
        throw Exception('No se puede conectar al servidor');
      }
      rethrow;
    } catch (e) {
      throw Exception('Error al obtener perfil: $e');
    }
  }

  /// Actualizar perfil del usuario
  /// SWAGGER-CORRECTED: PATCH /users/users/profile/
  Future<UserDetail> updateProfile({
    String? firstName,
    String? lastName,
    String? celular,
    String? fotoPerfil,
    String? razonSocial,
    String? numeroDocumentoFiscal,
  }) async {
    try {
      final data = <String, dynamic>{};

      if (firstName != null) data['first_name'] = firstName;
      if (lastName != null) data['last_name'] = lastName;
      if (celular != null) data['celular'] = celular;

      // Datos del profile anidado
      if (fotoPerfil != null ||
          razonSocial != null ||
          numeroDocumentoFiscal != null) {
        data['profile'] = <String, dynamic>{};
        if (fotoPerfil != null) data['profile']['foto_perfil'] = fotoPerfil;
        if (razonSocial != null) data['profile']['razon_social'] = razonSocial;
        if (numeroDocumentoFiscal != null) {
          data['profile']['numero_documento_fiscal'] = numeroDocumentoFiscal;
        }
      }

      final response = await _apiClient.dio.patch(
        '/users/users/profile/',
        data: data,
      );

      if (response.statusCode == 200) {
        return UserDetail.fromJson(response.data);
      } else {
        throw Exception('Error al actualizar perfil: ${response.statusCode}');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw Exception('No autorizado. Inicia sesión nuevamente');
      } else if (e.response?.statusCode == 400) {
        final message = e.response?.data['detail'] ?? 'Datos inválidos';
        throw Exception(message);
      } else if (e.type == DioExceptionType.connectionError) {
        throw Exception('No se puede conectar al servidor');
      }
      rethrow;
    } catch (e) {
      throw Exception('Error al actualizar perfil: $e');
    }
  }
}
