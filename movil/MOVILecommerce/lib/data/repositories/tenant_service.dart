import 'package:dio/dio.dart';
import '../api_client.dart';
import '../models/tenant_info.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Servicio para validar y obtener información de tiendas (Tenants)
class TenantService {
  final ApiClient _apiClient = ApiClient();

  /// Valida que una tienda existe consultando GET /api/tenant-info/
  /// usando el subdominio proporcionado
  ///
  /// Retorna TenantInfo si existe, null si no existe o hay error
  Future<TenantInfo?> validateTenant(String subdominio) async {
    try {
      // Configurar el ApiClient para usar este subdominio temporalmente
      await _apiClient.setTenant(subdominio);

      // Hacer la petición al endpoint tenant-info
      final response = await _apiClient.get('/tenant-info/');

      if (response.statusCode == 200 && response.data['type'] == 'tenant') {
        // La tienda existe y retorna sus datos
        final tenantData = response.data['data'];
        return TenantInfo.fromJson(tenantData);
      }

      // Si es tipo 'public', la tienda no existe
      return null;
    } on DioException catch (e) {
      print('Error validando tenant: ${e.message}');
      return null;
    } catch (e) {
      print('Error inesperado: $e');
      return null;
    }
  }

  /// Obtiene información del tenant actual
  Future<TenantInfo?> getCurrentTenantInfo() async {
    try {
      final response = await _apiClient.get('/tenant-info/');

      if (response.statusCode == 200 && response.data['type'] == 'tenant') {
        return TenantInfo.fromJson(response.data['data']);
      }
      return null;
    } on DioException catch (e) {
      print('Error obteniendo tenant info: ${e.message}');
      return null;
    }
  }

  /// Guarda el tenant seleccionado en SharedPreferences
  Future<void> saveTenant(String subdominio) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('selected_tenant', subdominio);
  }

  /// Obtiene el tenant guardado en SharedPreferences
  Future<String?> getSavedTenant() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('selected_tenant');
  }

  /// Limpia el tenant guardado
  Future<void> clearTenant() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('selected_tenant');
  }
}
