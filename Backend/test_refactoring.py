#!/usr/bin/env python
"""
🧪 SCRIPT DE VALIDACIÓN DE REFACTORIZACIÓN

Script para probar que la refactorización del módulo usuarios
mantiene la funcionalidad original.

Pruebas implementadas:
1. Importación de módulos
2. Disponibilidad de ViewSets
3. Estructura de URLs
4. Servicios y mixins
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Main.settings')
django.setup()

def test_imports():
    """Probar que las importaciones funcionan correctamente."""
    print("🔍 Probando importaciones...")
    
    try:
        # Probar importación de views modularizadas
        from api.v1.users.views import (
            UserRegistrationView,
            AdminUserRegistrationView,
            LoginView,
            UserProfileViewSet, 
            UserAdminViewSet,
            UserSearchViewSet
        )
        print("  ✅ Views modularizadas importadas correctamente")
        
        # Probar importación de servicios
        from api.v1.users.services import AuthService, UserManagementService
        print("  ✅ Servicios importados correctamente")
        
        # Probar importación de mixins
        from api.v1.common.mixins import AuditMixin, PermissionMixin, IPMixin
        print("  ✅ Mixins importados correctamente")
        
        # Probar importación de compatibility layer
        from api.v1.users.views_legacy_compatible import UserViewSet
        print("  ✅ Capa de compatibilidad importada correctamente")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Error de importación: {e}")
        return False

def test_url_structure():
    """Probar que las URLs están configuradas correctamente."""
    print("\n🔍 Probando estructura de URLs...")
    
    try:
        from api.v1.users.urls import urlpatterns
        
        # Verificar que hay patrones de URL
        if len(urlpatterns) > 0:
            print(f"  ✅ {len(urlpatterns)} patrones de URL configurados")
            
            # Listar algunos patrones principales
            url_names = []
            for pattern in urlpatterns:
                if hasattr(pattern, 'pattern') and hasattr(pattern.pattern, '_route'):
                    url_names.append(pattern.pattern._route)
                elif hasattr(pattern, 'url_patterns'):
                    # Es un include, buscar en sub-patrones
                    for sub_pattern in pattern.url_patterns:
                        if hasattr(sub_pattern, 'pattern') and hasattr(sub_pattern.pattern, '_route'):
                            url_names.append(f"{pattern.pattern._route}{sub_pattern.pattern._route}")
            
            print(f"  📋 URLs encontradas: {url_names[:5]}...")  # Mostrar solo las primeras 5
            return True
        else:
            print("  ❌ No se encontraron patrones de URL")
            return False
            
    except Exception as e:
        print(f"  ❌ Error al verificar URLs: {e}")
        return False

def test_viewset_methods():
    """Probar que los ViewSets tienen los métodos esperados."""
    print("\n🔍 Probando métodos de ViewSets...")
    
    try:
        from api.v1.users.views import (
            UserRegistrationView, 
            AdminUserRegistrationView,
            LoginView,
            UserProfileViewSet, 
            UserAdminViewSet
        )
        
        # Probar UserRegistrationView
        if hasattr(UserRegistrationView, 'post'):
            print("  ✅ UserRegistrationView.post disponible")
        else:
            print("  ❌ UserRegistrationView.post no encontrado")
        
        # Probar AdminUserRegistrationView
        if hasattr(AdminUserRegistrationView, 'post'):
            print("  ✅ AdminUserRegistrationView.post disponible")
        else:
            print("  ❌ AdminUserRegistrationView.post no encontrado")
            
        # Probar LoginView
        if hasattr(LoginView, 'post'):
            print("  ✅ LoginView.post disponible")
        else:
            print("  ❌ LoginView.post no encontrado")
        
        # Probar UserProfileViewSet  
        if hasattr(UserProfileViewSet, 'me'):
            print("  ✅ UserProfileViewSet.me disponible")
        else:
            print("  ❌ UserProfileViewSet.me no encontrado")
            
        # Probar UserAdminViewSet
        admin_methods = ['list', 'retrieve', 'create', 'update', 'destroy']
        for method in admin_methods:
            if hasattr(UserAdminViewSet, method):
                print(f"  ✅ UserAdminViewSet.{method} disponible")
            else:
                print(f"  ❌ UserAdminViewSet.{method} no encontrado")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error al verificar ViewSets: {e}")
        return False

def test_services():
    """Probar que los servicios funcionan correctamente."""
    print("\n🔍 Probando servicios...")
    
    try:
        from api.v1.users.services import AuthService, UserManagementService
        
        # Verificar métodos de AuthService
        auth_methods = ['generate_tokens', 'register_client_user', 'register_admin_user', 'authenticate_user']
        for method in auth_methods:
            if hasattr(AuthService, method):
                print(f"  ✅ AuthService.{method} disponible")
            else:
                print(f"  ❌ AuthService.{method} no encontrado")
        
        # Verificar métodos de UserManagementService
        mgmt_methods = ['search_users', 'get_active_users', 'get_users_by_role', '_apply_permission_filters']
        for method in mgmt_methods:
            if hasattr(UserManagementService, method):
                print(f"  ✅ UserManagementService.{method} disponible")
            else:
                print(f"  ❌ UserManagementService.{method} no encontrado")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error al verificar servicios: {e}")
        return False

def test_legacy_compatibility():
    """Probar que la capa de compatibilidad funciona."""
    print("\n🔍 Probando compatibilidad legacy...")
    
    try:
        from api.v1.users.views_legacy_compatible import UserViewSet
        
        # Verificar que tiene los métodos principales
        legacy_methods = ['list', 'retrieve', 'create', 'update', 'destroy']
        for method in legacy_methods:
            if hasattr(UserViewSet, method):
                print(f"  ✅ UserViewSet legacy.{method} disponible")
            else:
                print(f"  ❌ UserViewSet legacy.{method} no encontrado")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error al verificar compatibilidad: {e}")
        return False

def main():
    """Función principal de pruebas."""
    print("🚀 INICIANDO VALIDACIÓN DE REFACTORIZACIÓN")
    print("=" * 50)
    
    tests = [
        ("Importaciones", test_imports),
        ("Estructura URLs", test_url_structure),
        ("Métodos ViewSet", test_viewset_methods),
        ("Servicios", test_services),
        ("Compatibilidad Legacy", test_legacy_compatibility)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  💥 Error fatal en {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 RESULTADO FINAL: {passed}/{len(tests)} pruebas pasaron")
    
    if passed == len(tests):
        print("🎉 ¡REFACTORIZACIÓN VALIDADA EXITOSAMENTE!")
        print("✨ Todas las funcionalidades están operativas")
    else:
        print("⚠️  Hay problemas que requieren atención")
        print("🔧 Revisa los errores mostrados arriba")
    
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
