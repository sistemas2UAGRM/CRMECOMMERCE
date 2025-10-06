# Backend/test_empleados_api.py
"""
Script para probar los nuevos endpoints de empleados
"""

import requests
import json

# Configuración
BASE_URL = "http://127.0.0.1:8000/api/v1"
LOGIN_URL = f"{BASE_URL}/users/login/"
EMPLOYEES_URL = f"{BASE_URL}/users/search/employees/"
ROLES_URL = f"{BASE_URL}/users/search/roles/"

# Credenciales de prueba (usar admin)
ADMIN_CREDENTIALS = {
    "email": "admin@test.com",  # Cambiar por credenciales reales
    "password": "admin123"      # Cambiar por contraseña real
}

def test_empleados_endpoints():
    """
    Función principal de testing
    """
    print("🔍 Iniciando pruebas de endpoints de empleados...")
    
    # 1. Hacer login
    print("\n1️⃣ Probando login...")
    login_response = requests.post(LOGIN_URL, json=ADMIN_CREDENTIALS)
    
    if login_response.status_code != 200:
        print(f"❌ Error en login: {login_response.status_code}")
        print(f"Respuesta: {login_response.text}")
        return
    
    token = login_response.json().get('access')
    headers = {'Authorization': f'Bearer {token}'}
    print(f"✅ Login exitoso. Token obtenido.")
    
    # 2. Probar endpoint de empleados
    print("\n2️⃣ Probando endpoint de empleados...")
    employees_response = requests.get(EMPLOYEES_URL, headers=headers)
    
    if employees_response.status_code == 200:
        data = employees_response.json()
        print(f"✅ Empleados obtenidos: {data.get('count', 0)} encontrados")
        print(f"📄 Páginas: {data.get('num_pages', 1)}")
        
        if data.get('results'):
            print("👥 Primer empleado:")
            first_employee = data['results'][0]
            print(f"   - Nombre: {first_employee.get('first_name')} {first_employee.get('last_name')}")
            print(f"   - Email: {first_employee.get('email')}")
            print(f"   - Roles: {[g['name'] for g in first_employee.get('groups', [])]}")
    else:
        print(f"❌ Error al obtener empleados: {employees_response.status_code}")
        print(f"Respuesta: {employees_response.text}")
    
    # 3. Probar endpoint de roles
    print("\n3️⃣ Probando endpoint de roles...")
    roles_response = requests.get(ROLES_URL, headers=headers)
    
    if roles_response.status_code == 200:
        roles_data = roles_response.json()
        print(f"✅ Roles obtenidos: {roles_data.get('total_roles', 0)}")
        for role in roles_data.get('roles', []):
            print(f"   - {role['name']} (ID: {role['id']})")
    else:
        print(f"❌ Error al obtener roles: {roles_response.status_code}")
        print(f"Respuesta: {roles_response.text}")
    
    # 4. Probar filtros
    print("\n4️⃣ Probando filtros...")
    
    # Filtro por búsqueda
    search_params = {'search': 'admin'}
    search_response = requests.get(EMPLOYEES_URL, headers=headers, params=search_params)
    if search_response.status_code == 200:
        search_data = search_response.json()
        print(f"✅ Búsqueda 'admin': {search_data.get('count', 0)} resultados")
    
    # Filtro por activos
    active_params = {'active_only': 'true'}
    active_response = requests.get(EMPLOYEES_URL, headers=headers, params=active_params)
    if active_response.status_code == 200:
        active_data = active_response.json()
        print(f"✅ Empleados activos: {active_data.get('count', 0)} encontrados")
    
    print("\n🎉 Pruebas completadas!")

if __name__ == "__main__":
    try:
        test_empleados_endpoints()
    except Exception as e:
        print(f"💥 Error durante las pruebas: {e}")
        print("\n💡 Asegúrate de que:")
        print("   - El servidor Django esté ejecutándose (python manage.py runserver)")
        print("   - Las credenciales sean correctas")
        print("   - Los endpoints estén disponibles")