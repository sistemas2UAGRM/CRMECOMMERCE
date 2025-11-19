import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ApiClient {
  static final ApiClient _instance = ApiClient._internal();
  late Dio dio;
  final FlutterSecureStorage _storage = const FlutterSecureStorage();

  // MULTI-TENANT: Almacenar subdominio actual
  String? _currentTenant;

  factory ApiClient() {
    return _instance;
  }

  ApiClient._internal() {
    dio = Dio(
      BaseOptions(
        // MULTI-TENANT: baseUrl sin subdominio por defecto
        // Se configurará dinámicamente con setTenant()
        baseUrl: 'http://20.171.166.152:8000/api',
        connectTimeout: const Duration(seconds: 30),
        receiveTimeout: const Duration(seconds: 30),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    // Añadir interceptor de autenticación JWT
    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          // SWAGGER-CORRECTED: Rutas públicas actualizadas según endpoints reales
          final publicRoutes = [
            '/users/auth/login',
            '/users/auth/signup',
            '/users/auth/resend-verification',
          ];

          // Verificar si la ruta actual es pública
          final isPublicRoute = publicRoutes.any(
            (route) => options.path.contains(route),
          );

          if (!isPublicRoute) {
            // Obtener el token de flutter_secure_storage
            final token = await _storage.read(key: 'auth_token');

            if (token != null && token.isNotEmpty) {
              // Añadir el token al header Authorization
              options.headers['Authorization'] = 'Bearer $token';
            }
          }

          return handler.next(options);
        },
        onResponse: (response, handler) {
          return handler.next(response);
        },
        onError: (DioException error, handler) async {
          // Manejar errores de autenticación
          if (error.response?.statusCode == 401) {
            // Token expirado o inválido - eliminar token
            await _storage.delete(key: 'auth_token');
            // Aquí podrías redirigir al usuario a la pantalla de login
          }

          return handler.next(error);
        },
      ),
    );

    // Interceptor de logging para desarrollo
    dio.interceptors.add(
      LogInterceptor(
        requestBody: true,
        responseBody: true,
        error: true,
        requestHeader: true,
        responseHeader: false,
      ),
    );
  }

  // Métodos helper para facilitar las peticiones
  Future<Response> get(String path, {Map<String, dynamic>? queryParameters}) {
    return dio.get(path, queryParameters: queryParameters);
  }

  Future<Response> post(String path, {dynamic data}) {
    return dio.post(path, data: data);
  }

  Future<Response> put(String path, {dynamic data}) {
    return dio.put(path, data: data);
  }

  Future<Response> delete(String path, {dynamic data}) {
    return dio.delete(path, data: data);
  }

  // Método para guardar el token
  Future<void> saveToken(String token) async {
    await _storage.write(key: 'auth_token', value: token);
  }

  // Método para obtener el token
  Future<String?> getToken() async {
    return await _storage.read(key: 'auth_token');
  }

  // Método para eliminar el token (logout)
  Future<void> clearToken() async {
    await _storage.delete(key: 'auth_token');
  }

  // MULTI-TENANT: Configurar tenant dinámicamente
  /// Configura el subdominio del tenant y actualiza el baseUrl
  ///
  /// Para emulador Android usamos 10.0.2.2 (IP del host desde el emulador)
  /// El backend lee el tenant del Host header
  Future<void> setTenant(String subdominio) async {
    _currentTenant = subdominio;

    // Actualizar baseUrl - usar 10.0.2.2 para emulador Android
    // Para dispositivo físico cambiar a IP local (ej: 192.168.1.XX)
    final newBaseUrl = 'http://20.171.166.152:8000/api';

    dio.options.baseUrl = newBaseUrl;

    // IMPORTANTE: Agregar Host header con el subdominio para django-tenants
    dio.options.headers['Host'] = '$subdominio.20.171.166.152:8000';

    print('✅ Tenant configurado: $subdominio');
    print('✅ Nueva baseUrl: $newBaseUrl');
    print('✅ Host header: $subdominio.20.171.166.152:8000');
  }

  /// Obtiene el tenant actual configurado
  String? getCurrentTenant() {
    return _currentTenant;
  }

  /// Limpia la configuración del tenant
  Future<void> clearTenant() async {
    _currentTenant = null;
    dio.options.baseUrl = 'http://20.171.166.152:8000/api'; // URL por defecto
  }
}
