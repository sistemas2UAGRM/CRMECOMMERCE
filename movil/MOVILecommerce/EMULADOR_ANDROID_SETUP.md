# 🔧 Configuración para Emulador Android + Backend Localhost

## ⚠️ Problema

El emulador Android **NO puede resolver** `pepita.localhost` porque:
- El DNS del emulador no resuelve subdominios de localhost
- `localhost` dentro del emulador apunta al propio emulador, no a tu PC

## ✅ Solución: IP 10.0.2.2 + Host Header

### Cómo Funciona

1. **IP 10.0.2.2**: IP especial del emulador que apunta a tu PC (127.0.0.1 del host)
2. **Host Header**: Django-tenants lee el subdominio del header `Host`

```dart
// La petición va a:
baseUrl: 'http://10.0.2.2:8000/api'

// Pero con header:
Host: pepita.localhost:8000

// Django-tenants detecta "pepita" del Host header
```

### Configuración Actual del Código

El código ya está configurado automáticamente:

```dart
// lib/data/api_client.dart
final newBaseUrl = 'http://10.0.2.2:8000/api';
dio.options.headers['Host'] = '$subdominio.localhost:8000';
```

### ✅ NO necesitas adb reverse

Con esta configuración, **no se requiere** `adb reverse`.

---

## 🔄 Flujo Completo

### 1. Backend Django corriendo
```bash
cd backend
python manage.py runserver 0.0.0.0:8000
```

### 2. Verificar que el tenant existe (desde tu PC)
```bash
# Desde Postman o navegador en tu PC
GET http://pepita.localhost:8000/api/tenant-info/

# Respuesta esperada:
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

### 3. Ejecutar Flutter
```bash
flutter run
```

### 4. Usar la app
1. Ingresa "pepita" en la pantalla de selección
2. Presiona "Continuar"
3. ✅ La app conecta a `http://10.0.2.2:8000/api` con `Host: pepita.localhost:8000`

---

## 🐛 Solución de Problemas

### Error: "Connection refused"

**Causa:** El backend no está corriendo o no escucha en todas las interfaces.

**Solución:**
```bash
python manage.py runserver 0.0.0.0:8000  # ✅ Correcto
# NO usar: python manage.py runserver (solo 127.0.0.1)
```

### Error: "No se encontró la tienda"

**Causa 1:** El tenant no existe en el backend.

**Solución:** Crear el tenant desde Django shell:
```python
python manage.py shell
```
```python
from apps.tenants.models import Client, Domain

tenant = Client.objects.create(
    schema_name='pepita',
    name='Boutique Pepita'
)

Domain.objects.create(
    domain='pepita.localhost',
    tenant=tenant,
    is_primary=True
)
```

**Causa 2:** El backend no está corriendo en `0.0.0.0:8000`

**Solución:**
```bash
python manage.py runserver 0.0.0.0:8000  # ✅ Correcto
```

### Error: "Host header poisoning" o tipo "public"

**Causa:** Django-tenants no reconoce el Host header.

**Solución:** Verificar `settings.py`:
```python
ALLOWED_HOSTS = [
    '.localhost',
    '127.0.0.1',
    '10.0.2.2',  # ✅ Importante para emulador
    'localhost',
    '*',
]
```

---

## 🔍 Cómo Funciona Internamente

```
1. Usuario ingresa "pepita" en Flutter
   ↓
2. ApiClient.setTenant("pepita")
   - baseUrl = "http://10.0.2.2:8000/api"
   - headers['Host'] = "pepita.localhost:8000"
   ↓
3. Flutter hace: GET http://10.0.2.2:8000/api/tenant-info/
   Con header: Host: pepita.localhost:8000
   ↓
4. Django recibe la petición en 0.0.0.0:8000
   ↓
5. Django-tenants middleware lee: Host: pepita.localhost:8000
   ↓
6. Extrae "pepita" → Cambia a ESQUEMA "pepita"
   ↓
7. Retorna datos del tenant "pepita"
```

## 🌐 Alternativas

### Para Dispositivo Físico (misma WiFi)

Si usas un dispositivo real conectado a la misma red:

1. Obtén la IP de tu PC:
```bash
# Windows
ipconfig
# Busca IPv4 (ej: 192.168.1.105)
```

2. Modifica `ApiClient.setTenant()`:
```dart
final newBaseUrl = 'http://192.168.1.105:8000/api';
dio.options.headers['Host'] = '$subdominio.localhost:8000';
```

3. Modifica `settings.py`:
```python
ALLOWED_HOSTS = ['192.168.1.105', '.localhost', '*']
```

### Usar ngrok (para testing remoto)

```bash
ngrok http 8000
```

Obtienes una URL pública como `https://abc123.ngrok-free.app`

Modifica `ApiClient.setTenant()`:
```dart
final newBaseUrl = 'https://abc123.ngrok-free.app/api';
dio.options.headers['Host'] = '$subdominio.localhost';
```

---

## 📋 Checklist de Verificación

Antes de ejecutar la app Flutter, verifica:

- [ ] Backend corriendo: `python manage.py runserver 0.0.0.0:8000`
- [ ] Tenant creado en Django con domain `pepita.localhost`
- [ ] Endpoint accesible desde tu PC: `http://pepita.localhost:8000/api/tenant-info/`
- [ ] `ALLOWED_HOSTS` incluye `'10.0.2.2'` y `'.localhost'`
- [ ] CORS configurado correctamente

---

## 🎯 Comandos Rápidos

```bash
# 1. Iniciar backend
cd backend
python manage.py runserver 0.0.0.0:8000

# 2. Ejecutar Flutter (en otra terminal)
cd MOVILecommerce
flutter run
```

---

✅ **Con esta configuración (IP 10.0.2.2 + Host header), tu app Flutter funciona perfectamente con el backend localhost multi-tenant sin necesidad de adb reverse.**
