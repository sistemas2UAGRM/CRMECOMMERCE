import 'package:flutter/material.dart';
import '../data/models/tenant_info.dart';
import '../data/repositories/tenant_service.dart';

/// Provider para gestionar el estado del Tenant (Tienda seleccionada)
class TenantProvider with ChangeNotifier {
  final TenantService _tenantService = TenantService();

  TenantInfo? _currentTenant;
  bool _isLoading = false;
  String? _errorMessage;

  TenantInfo? get currentTenant => _currentTenant;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  bool get hasTenant => _currentTenant != null;

  /// Inicializa el provider verificando si hay un tenant guardado
  Future<void> initialize() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      // Verificar si hay un tenant guardado previamente
      final savedTenant = await _tenantService.getSavedTenant();

      if (savedTenant != null && savedTenant.isNotEmpty) {
        // Validar que el tenant aún existe
        final tenantInfo = await _tenantService.validateTenant(savedTenant);

        if (tenantInfo != null) {
          _currentTenant = tenantInfo;
          print('✅ Tenant restaurado: ${tenantInfo.name}');
        } else {
          // El tenant guardado ya no existe, limpiar
          await _tenantService.clearTenant();
          print('⚠️ Tenant guardado no válido, limpiando...');
        }
      }
    } catch (e) {
      print('❌ Error inicializando tenant: $e');
      _errorMessage = 'Error al inicializar la tienda';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Selecciona y valida un tenant
  Future<bool> selectTenant(String subdominio) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      // Normalizar el subdominio (minúsculas, sin espacios)
      final normalizedSubdominio = subdominio.trim().toLowerCase();

      if (normalizedSubdominio.isEmpty) {
        _errorMessage = 'Por favor ingresa el nombre de la tienda';
        _isLoading = false;
        notifyListeners();
        return false;
      }

      // Validar que la tienda existe
      final tenantInfo =
          await _tenantService.validateTenant(normalizedSubdominio);

      if (tenantInfo != null) {
        // Tienda válida, guardar
        _currentTenant = tenantInfo;
        await _tenantService.saveTenant(normalizedSubdominio);

        _isLoading = false;
        notifyListeners();

        print('✅ Tienda seleccionada: ${tenantInfo.name}');
        return true;
      } else {
        // Tienda no existe
        _errorMessage = 'No se encontró la tienda "$normalizedSubdominio"';
        _isLoading = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      print('❌ Error seleccionando tenant: $e');
      _errorMessage = 'Error al conectar con la tienda';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// Limpia el tenant actual y cierra sesión completa
  Future<void> clearTenant() async {
    _currentTenant = null;
    _errorMessage = null;
    await _tenantService.clearTenant();
    notifyListeners();
    print('✅ Tenant limpiado');
  }

  /// Limpia solo el mensaje de error
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }
}
