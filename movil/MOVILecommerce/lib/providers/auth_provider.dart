import 'package:flutter/foundation.dart';
import '../data/models/user_detail.dart';
import '../data/repositories/auth_service.dart';
import '../data/repositories/profile_service.dart';

// SWAGGER-CORRECTED: AuthProvider actualizado sin FCM
class AuthProvider extends ChangeNotifier {
  final AuthService _authService = AuthService();
  final ProfileService _profileService = ProfileService();

  UserDetail? _currentUser;
  bool _isAuthenticated = false;
  bool _isLoading = false;
  String? _errorMessage;

  UserDetail? get currentUser => _currentUser;
  bool get isAuthenticated => _isAuthenticated;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  // Inicializar - Verifica si hay sesión guardada y obtiene perfil
  Future<void> initialize() async {
    _isLoading = true;
    notifyListeners();

    try {
      // Verificar si hay un token guardado
      final token = await _authService.getStoredToken();

      if (token != null && token.isNotEmpty) {
        // Hay sesión guardada, obtener datos del usuario
        _currentUser = await _profileService.getProfile();
        _isAuthenticated = true;
      } else {
        // No hay sesión
        _currentUser = null;
        _isAuthenticated = false;
      }
    } catch (e) {
      debugPrint('Error al inicializar sesión: $e');
      _currentUser = null;
      _isAuthenticated = false;
      // Si falla, limpiar token potencialmente inválido
      await _authService.logout();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // Login
  // SWAGGER-CORRECTED: Usa el objeto user que viene en la respuesta del login
  Future<bool> login(String email, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final loginResponse = await _authService.login(email, password);

      // El backend retorna el usuario en la respuesta del login
      final userData = loginResponse['data']['user'];
      if (userData != null) {
        _currentUser = UserDetail.fromJson(userData);
      } else {
        // Fallback: obtener perfil si no viene en la respuesta
        _currentUser = await _profileService.getProfile();
      }

      _isAuthenticated = true;
      _isLoading = false;
      _errorMessage = null;
      notifyListeners();

      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      _isAuthenticated = false;
      _currentUser = null;
      notifyListeners();
      return false;
    }
  }

  // Register
  // SWAGGER-CORRECTED: NO inicia sesión automáticamente, usuario debe verificar email
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
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final result = await _authService.register(
        email: email,
        password: password,
        passwordConfirm: passwordConfirm,
        username: username,
        firstName: firstName,
        lastName: lastName,
        fechaNacimiento: fechaNacimiento,
        sexo: sexo,
        celular: celular,
        aceptaTerminos: aceptaTerminos,
        aceptaMarketing: aceptaMarketing,
      );

      _isLoading = false;
      notifyListeners();

      return {
        'success': true,
        'message': result['message'],
      };
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      notifyListeners();

      return {
        'success': false,
        'message': _errorMessage,
      };
    }
  }

  // Reenviar correo de verificación
  Future<bool> resendVerification(String email) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      await _authService.resendVerification(email);
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  // Logout
  Future<void> logout() async {
    try {
      await _authService.logout();
    } catch (e) {
      // Ignorar errores de logout, siempre limpiar el estado local
      debugPrint('Error durante logout: $e');
    } finally {
      _currentUser = null;
      _isAuthenticated = false;
      _errorMessage = null;
      notifyListeners();
    }
  }

  // Actualizar perfil de usuario
  Future<bool> updateProfile({
    String? firstName,
    String? lastName,
    String? celular,
    String? fotoPerfil,
    String? razonSocial,
    String? numeroDocumentoFiscal,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _currentUser = await _profileService.updateProfile(
        firstName: firstName,
        lastName: lastName,
        celular: celular,
        fotoPerfil: fotoPerfil,
        razonSocial: razonSocial,
        numeroDocumentoFiscal: numeroDocumentoFiscal,
      );

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  // Limpiar mensaje de error
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
}
