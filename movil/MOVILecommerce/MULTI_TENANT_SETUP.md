# 🏪 Sistema Multi-Tenant Implementado

## 📋 Descripción General

Se ha implementado un sistema multi-tenant que permite a la aplicación Flutter conectarse a diferentes tiendas del backend Django según el subdominio seleccionado.

## 🔄 Flujo de Funcionamiento

### 1. **Inicio de la Aplicación**
```
Usuario abre la app → TenantSelectionView (pantalla de selección de tienda)
```

### 2. **Selección de Tienda**
```
Usuario ingresa "pepita" → Se valida con GET /api/tenant-info/ 
→ Si existe: Guarda tenant y redirige al Home
→ Si no existe: Muestra error "No se encontró la tienda"
```

### 3. **Navegación Normal**
```
Home → Productos → Carrito → Checkout
(Todas las peticiones usan: http://pepita.10.0.2.2.nip.io:8000/api)
```

### 4. **Cambio de Tienda**
```
Usuario presiona icono 🏪 → Confirma cambio 
→ Limpia tenant + sesión → Regresa a TenantSelectionView
```

---

## 🗂️ Archivos Creados/Modificados

### ✅ Nuevos Archivos

1. **`lib/data/models/tenant_info.dart`**
   - Modelo para información de la tienda
   - Campos: `name`, `schemaName`, `createdOn`, `domainUrl`

2. **`lib/data/repositories/tenant_service.dart`**
   - Servicio para validar tiendas
   - Métodos:
     - `validateTenant(subdominio)` - Valida que la tienda existe
     - `getCurrentTenantInfo()` - Obtiene info del tenant actual
     - `saveTenant()` / `getSavedTenant()` / `clearTenant()`

3. **`lib/providers/tenant_provider.dart`**
   - Provider para gestionar estado del tenant
   - Estados: `currentTenant`, `isLoading`, `errorMessage`
   - Métodos:
     - `initialize()` - Restaura tenant guardado al iniciar
     - `selectTenant(subdominio)` - Valida y selecciona tienda
     - `clearTenant()` - Limpia tenant

4. **`lib/features/tenant/tenant_selection_view.dart`**
   - Pantalla inicial para seleccionar tienda
   - Input de texto con validación
   - Muestra errores si la tienda no existe

### ✅ Archivos Modificados

1. **`lib/data/api_client.dart`**
   - Añadido: `_currentTenant` (subdominio actual)
   - Nuevo método: `setTenant(subdominio)` - Actualiza `baseUrl` dinámicamente
   - Nuevo método: `getCurrentTenant()` - Obtiene tenant actual
   - Nuevo método: `clearTenant()` - Limpia configuración

2. **`lib/main.dart`**
   - Añadido: `TenantProvider` a `MultiProvider`
   - Cambiado: `initialLocation: '/tenant-selection'`
   - Nueva ruta: `/tenant-selection`

3. **`lib/features/home/home_view.dart`**
   - Título del AppBar muestra nombre de la tienda
   - Nuevo botón 🏪 para cambiar de tienda
   - Importado: `TenantProvider`

---

## 🌐 URLs y Subdominios

### Desarrollo (Emulador Android)

El sistema usa **localhost** con subdominios:

```dart
// Tienda "pepita"
http://pepita.localhost:8000/api

// Tienda "mitienda"
http://mitienda.localhost:8000/api
```

### ⚠️ Configuración Especial para Emulador Android

Dado que el emulador Android no puede acceder directamente a `localhost` de la máquina host, necesitas usar **proxy inverso** o **túnel**:

**Opción 1: adb reverse (Recomendada)**
```bash
adb reverse tcp:8000 tcp:8000
```
Esto mapea el puerto 8000 del emulador al puerto 8000 de tu máquina.

**Opción 2: Usar la IP 10.0.2.2**
Modifica temporalmente para desarrollo:
```dart
final newBaseUrl = 'http://$subdominio.10.0.2.2:8000/api';
```
Pero el backend debe aceptar `Host: pepita.10.0.2.2`

### Para Dispositivo Físico

Si usas un dispositivo real en la misma red WiFi, usa la IP local de tu computadora:

```dart
// Cambiar en ApiClient.setTenant():
final newBaseUrl = 'http://$subdominio.192.168.1.XX:8000/api';
```

Donde `192.168.1.XX` es la IP de tu computadora.

**Backend debe aceptar este host:**
```python
ALLOWED_HOSTS = ['.localhost', '192.168.1.XX', '*']
```

---

## 🔧 Configuración del Backend (Django)

### Requisitos

El backend debe estar configurado para aceptar peticiones de subdominios usando `nip.io`:

#### 1. Actualizar `ALLOWED_HOSTS` (settings.py)
```python
ALLOWED_HOSTS = [
    '.localhost',
    '127.0.0.1',
    '10.0.2.2',      # ✅ Para emulador Android
    'localhost',
    '*',
]
```

#### 2. Actualizar CORS (settings.py)
```python
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^http://.+\.localhost:8000$",              # Desarrollo localhost
    r"^http://.+\.10\.0\.2\.2:8000$",           # Emulador Android (alternativa)
    r"^http://.+\.192\.168\.\d+\.\d+:8000$",   # Dispositivo real
]
```

#### 3. Crear Tenant de Prueba

Desde el backend Django:

```bash
python manage.py shell
```

```python
from apps.tenants.models import Client, Domain

# Crear tenant "pepita"
tenant = Client.objects.create(
    schema_name='pepita',
    name='Boutique Pepita'  # Como muestra el backend
)

# Crear dominio (desarrollo)
Domain.objects.create(
    domain='pepita.localhost',
    tenant=tenant,
    is_primary=True
)
```

---

## 🧪 Cómo Probar

### Paso 1: Verificar Backend
```bash
# Terminal 1 - Ejecutar backend
cd backend
python manage.py runserver 0.0.0.0:8000
```

### Paso 2: Probar Endpoint (desde navegador o Postman)
```
http://pepita.localhost:8000/api/tenant-info/
```

**Respuesta esperada (según tu Postman):**
```json
{
  "type": "tenant",
  "data": {
    "name": "Boutique Pepita",
    "schema_name": "pepita",
    "created_on": "2025-11-18",
    "domain_url": "pepita.localhost"
  }
}
```

### Paso 3: Ejecutar la App
```bash
flutter run
```

### Paso 4: Usar la App
1. La app abrirá en **TenantSelectionView**
2. Ingresa `pepita` en el campo
3. Presiona **Continuar**
4. Si la tienda existe → Redirige al Home
5. Si no existe → Muestra error

---

## 🎯 Casos de Uso

### Caso 1: Primera vez usando la app
```
1. Usuario abre app
2. Ve pantalla de selección de tienda
3. Ingresa "pepita"
4. Sistema valida y guarda en SharedPreferences
5. Navega al Home
```

### Caso 2: Abre la app nuevamente
```
1. TenantProvider.initialize() lee tenant guardado
2. Valida que "pepita" aún existe
3. Configura ApiClient automáticamente
4. Usuario ve el Home directamente
```

### Caso 3: Cambiar de tienda
```
1. Usuario presiona 🏪 en el AppBar
2. Confirma que quiere cambiar
3. Sistema limpia tenant + sesión de usuario
4. Regresa a TenantSelectionView
5. Puede ingresar otra tienda (ej: "mitienda")
```

### Caso 4: Tienda eliminada del backend
```
1. Usuario abre app
2. TenantProvider intenta validar tenant guardado
3. Backend retorna type: "public" (no existe)
4. Sistema limpia tenant guardado
5. Muestra TenantSelectionView
```

---

## 🔒 Consideraciones de Seguridad

1. **Validación antes de usar**: Siempre se valida que la tienda existe antes de permitir acceso
2. **Token JWT separado por tenant**: Cada tienda tiene su propia base de datos de usuarios
3. **Cambio de tienda limpia sesión**: Al cambiar de tienda, se cierra sesión automáticamente

---

## 📝 Notas Importantes

### ⚠️ Problemas Comunes

#### 1. Emulador Android no puede acceder a localhost

**Solución: Usar adb reverse**
```bash
adb reverse tcp:8000 tcp:8000
```

#### 2. Dispositivo físico no puede acceder

**Solución: Usar IP local**
```dart
// Cambiar en setTenant():
final newBaseUrl = 'http://$subdominio.192.168.1.XX:8000/api';
```

#### 3. Usar ngrok para testing remoto

```bash
ngrok http 8000
```

Cambia baseUrl a la URL de ngrok y pasa tenant por header:
```dart
options.headers['X-Tenant'] = subdominio;
```

---

## 🚀 Próximos Pasos

- [ ] Implementar caché de tenants conocidos
- [ ] Añadir lista de "Tiendas Recientes"
- [ ] Logo personalizado por tenant
- [ ] Tema personalizado por tenant (colores)
- [ ] Modo offline con último tenant usado

---

## 🐛 Solución de Problemas

### Error: "No se encontró la tienda"
- Verifica que el tenant existe en el backend
- Prueba el endpoint manualmente: `http://pepita.10.0.2.2.nip.io:8000/api/tenant-info/`

### Error: "Connection refused"
- Verifica que el backend esté corriendo en `0.0.0.0:8000`
- Verifica que `ALLOWED_HOSTS` incluya `.nip.io`

### Error: CORS
- Añade el patrón correcto en `CORS_ALLOWED_ORIGIN_REGEXES`

---

**Implementación completada el:** 19 de Noviembre de 2025
