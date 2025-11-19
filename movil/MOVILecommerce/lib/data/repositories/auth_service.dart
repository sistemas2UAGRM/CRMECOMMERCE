import 'package:dio/dio.dart';
import '../api_client.dart';

// SWAGGER-CORRECTED: Servicio de autenticación con endpoints reales
/// Servicio de autenticación que maneja login, registro y verificación de email
class AuthService {
  final ApiClient _apiClient = ApiClient();

  /// Login de usuario
  /// SWAGGER-CORRECTED: POST /users/auth/login/
  /// Retorna un Map con 'access' (token JWT) y debe verificar que email esté verificado
  Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await _apiClient.post(
        '/users/auth/login/',
        data: {
          'email': email,
          'password': password,
        },
      );

      if (response.statusCode == 200) {
        // SWAGGER-CORRECTED: El backend retorna "access_token" no "access"
        final token = response.data['access_token']; // JWT token

        // Guardar el token en flutter_secure_storage
        await _apiClient.saveToken(token);

        return {
          'token': token,
          'data': response.data,
        };
      } else {
        throw DioException(
          requestOptions: response.requestOptions,
          response: response,
          type: DioExceptionType.badResponse,
          error: 'Login falló con código: ${response.statusCode}',
        );
      }
    } on DioException catch (e) {
      // Manejar errores específicos de Dio
      if (e.response?.statusCode == 401) {
        throw Exception('Credenciales inválidas');
      } else if (e.response?.statusCode == 403) {
        // Email no verificado
        throw Exception('Debes verificar tu email antes de iniciar sesión');
      } else if (e.response?.statusCode == 400) {
        final message = e.response?.data['detail'] ??
            e.response?.data['message'] ??
            'Email o contraseña faltante';
        throw Exception(message);
      } else if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw Exception('Tiempo de espera agotado. Verifica tu conexión');
      } else if (e.type == DioExceptionType.connectionError) {
        throw Exception('No se puede conectar al servidor');
      }
      rethrow;
    } catch (e) {
      throw Exception('Error inesperado durante el login: $e');
    }
  }

  /// Registro de nuevo usuario
  /// SWAGGER-CORRECTED: POST /users/auth/signup/
  /// El usuario NO puede loguearse hasta verificar su email
  Future<Map<String, dynamic>> register({
    required String email,
    required String password,
    required String passwordConfirm,
    required String username,
    required String firstName,
    required String lastName,
    required String fechaNacimiento,
    required String sexo,
    required String celular,
    bool aceptaTerminos = true,
    bool aceptaMarketing = false,
  }) async {
    try {
      final response = await _apiClient.post(
        '/users/auth/signup/',
        data: {
          'email': email,
          'password': password,
          'password_confirm': passwordConfirm,
          'username': username,
          'first_name': firstName,
          'last_name': lastName,
          'fecha_de_nacimiento': fechaNacimiento,
          'sexo': sexo,
          'celular': celular,
          'acepta_terminos': aceptaTerminos,
          'acepta_marketing': aceptaMarketing,
        },
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        // NO guardamos token porque el usuario no está verificado
        return {
          'success': true,
          'message': 'Registro exitoso. Verifica tu email para continuar.',
          'data': response.data,
        };
      } else {
        throw DioException(
          requestOptions: response.requestOptions,
          response: response,
          type: DioExceptionType.badResponse,
          error: 'Registro falló con código: ${response.statusCode}',
        );
      }
    } on DioException catch (e) {
      // Manejar errores específicos de Dio
      if (e.response?.statusCode == 409 || e.response?.statusCode == 400) {
        final message = e.response?.data['detail'] ??
            e.response?.data['email']?.first ??
            e.response?.data['username']?.first ??
            'Este email o username ya está registrado';
        throw Exception(message);
      } else if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw Exception('Tiempo de espera agotado. Verifica tu conexión');
      } else if (e.type == DioExceptionType.connectionError) {
        throw Exception('No se puede conectar al servidor');
      }
      rethrow;
    } catch (e) {
      throw Exception('Error inesperado durante el registro: $e');
    }
  }

  /// Reenviar correo de verificación
  /// SWAGGER-CORRECTED: POST /users/auth/resend-verification/
  Future<void> resendVerification(String email) async {
    try {
      final response = await _apiClient.post(
        '/users/auth/resend-verification/',
        data: {
          'email': email,
        },
      );

      if (response.statusCode != 200 && response.statusCode != 201) {
        throw Exception('Error al reenviar correo de verificación');
      }
    } on DioException catch (e) {
      if (e.response?.statusCode == 400) {
        final message = e.response?.data['detail'] ??
            'El email ya está verificado o no existe';
        throw Exception(message);
      } else if (e.type == DioExceptionType.connectionError) {
        throw Exception('No se puede conectar al servidor');
      }
      rethrow;
    } catch (e) {
      throw Exception('Error al reenviar verificación: $e');
    }
  }

  /// Logout de usuario
  /// Elimina el token guardado localmente
  Future<void> logout() async {
    try {
      // Eliminar el token de flutter_secure_storage
      await _apiClient.clearToken();
    } catch (e) {
      // Aunque falle, eliminar el token local
      await _apiClient.clearToken();
      throw Exception('Error durante el logout: $e');
    }
  }

  /// Verificar si el usuario está autenticado
  /// Retorna true si existe un token guardado
  Future<bool> isAuthenticated() async {
    final token = await _apiClient.getToken();
    return token != null && token.isNotEmpty;
  }

  /// Obtener el token almacenado
  Future<String?> getStoredToken() async {
    return await _apiClient.getToken();
  }
}
