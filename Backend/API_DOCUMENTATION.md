# 📚 API CRM+Ecommerce - Sprint 1 Documentation Completa

## 🚀 Implementación Completada

### **✅ Módulos Implementados**

1. **👥 USUARIOS (Users)**
   - Autenticación con JWT
   - Registro público y por administrador
   - Gestión de perfiles
   - Búsquedas y estadísticas

2. **🔐 CRM (Roles y Permisos)**
   - Gestión de roles jerárquicos
   - Asignación de permisos
   - Control de acceso granular

3. **📊 BITÁCORA (Auditoría)**
   - Registro automático de acciones
   - Consultas con filtros avanzados
   - Estadísticas y exportación

4. **🛍️ E-COMMERCE (Productos y Carritos)**
   - Catálogo de productos con categorías
   - Gestión de stock en tiempo real
   - Carritos de compra personalizados
   - Filtros por estado de disponibilidad

---

## 🌐 Endpoints Principales

### **AUTENTICACIÓN**
```
POST /api/v1/users/register/          # Registro público (clientes)
POST /api/v1/users/admin-register/    # Registro por administrador
POST /api/v1/users/login/             # Login con JWT
```

### **GESTIÓN DE USUARIOS**
```
GET  /api/v1/users/                   # Listar usuarios
GET  /api/v1/users/profile/           # Perfil del usuario actual
PUT  /api/v1/users/profile/           # Actualizar perfil
GET  /api/v1/users/search/?q=juan     # Buscar usuarios
GET  /api/v1/users/active/            # Usuarios activos
GET  /api/v1/users/stats/             # Estadísticas
GET  /api/v1/users/by-role/vendedor/  # Usuarios por rol
```

### **GESTIÓN CRM**
```
GET  /api/v1/crm/roles/               # Listar roles
GET  /api/v1/crm/roles/1/permissions/ # Permisos de un rol
PUT  /api/v1/crm/roles/1/permissions/ # Actualizar permisos
POST /api/v1/crm/assign-role/5/       # Asignar roles a usuario
GET  /api/v1/crm/users-by-role/admin/ # Usuarios por rol
GET  /api/v1/crm/permisos/            # Listar permisos
```

### **AUDITORÍA**
```
GET  /api/v1/common/bitacora/         # Consultar bitácora
GET  /api/v1/common/bitacora/stats/   # Estadísticas
GET  /api/v1/common/bitacora/export/  # Exportar registros
```

### **E-COMMERCE**
```
# CATÁLOGO
GET  /api/v1/ecommerce/productos/     # Listar productos (catálogo)
GET  /api/v1/ecommerce/productos/1/   # Detalle de producto
GET  /api/v1/ecommerce/categorias/    # Listar categorías
GET  /api/v1/ecommerce/categorias/1/productos/ # Productos por categoría

# GESTIÓN (Admin/Supervisor)
POST /api/v1/ecommerce/productos/     # Crear producto
PUT  /api/v1/ecommerce/productos/1/stock/ # Actualizar stock
GET  /api/v1/ecommerce/productos/stats/ # Estadísticas

# FILTROS
GET  /api/v1/ecommerce/productos/por-estado/?estado=disponible # Disponibles
GET  /api/v1/ecommerce/productos/por-estado/?estado=agotado    # Agotados
GET  /api/v1/ecommerce/productos/por-estado/?estado=no_disponible # Inactivos

# CARRITOS
GET  /api/v1/ecommerce/carritos/mi-carrito/ # Mi carrito actual
POST /api/v1/ecommerce/carritos/1/productos/ # Agregar al carrito
```

---

## 🔑 Autenticación JWT

### **Login**
```bash
curl -X POST http://localhost:8000/api/v1/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@empresa.com",
    "password": "password123"
  }'
```

**Respuesta:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@empresa.com",
    "groups": ["administrador"],
    "permissions": ["view_user", "add_user", ...]
  }
}
```

### **Usar Token**
```bash
curl -X GET http://localhost:8000/api/v1/users/profile/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

---

## 👤 Roles del Sistema

### **🔴 Administrador (Gerente)**
- **Permisos**: Acceso completo al sistema
- **Puede**: Crear usuarios, asignar roles, ver toda la bitácora
- **Endpoints**: Todos los disponibles

### **🟡 Empleado Nivel 1 (Supervisor)**
- **Permisos**: Gestión de equipo y supervisión
- **Puede**: Ver usuarios de su equipo, consultar bitácora limitada
- **Endpoints**: Usuarios, CRM (lectura), Bitácora (filtrada)

### **🟢 Empleado Nivel 2 (Vendedor)**
- **Permisos**: Operaciones de venta
- **Puede**: Ver su perfil, consultar su bitácora
- **Endpoints**: Perfil, Bitácora propia

### **🔵 Cliente**
- **Permisos**: Acceso básico
- **Puede**: Gestionar su perfil
- **Endpoints**: Perfil, Registro

---

## 📋 Ejemplos de Uso

### **1. Registro de Cliente**
```bash
curl -X POST http://localhost:8000/api/v1/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "juan.cliente",
    "email": "juan@gmail.com",
    "password": "MiPassword123!",
    "password_confirm": "MiPassword123!",
    "first_name": "Juan",
    "last_name": "Pérez",
    "acepta_terminos": true
  }'
```

### **2. Crear Usuario por Administrador**
```bash
curl -X POST http://localhost:8000/api/v1/users/admin-register/ \
  -H "Authorization: Bearer TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "maria.vendedora",
    "email": "maria@empresa.com",
    "first_name": "María",
    "last_name": "González",
    "rol": "empleadonivel2",
    "send_welcome_email": true
  }'
```

### **3. Asignar Roles**
```bash
curl -X POST http://localhost:8000/api/v1/crm/assign-role/5/ \
  -H "Authorization: Bearer TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{
    "roles": [2, 3],
    "motivo": "Promoción a supervisor"
  }'
```

### **4. Consultar Bitácora**
```bash
curl -X GET "http://localhost:8000/api/v1/common/bitacora/?fecha_inicio=2024-01-01&usuario_id=5" \
  -H "Authorization: Bearer TOKEN_ADMIN"
```

---

## 🔧 Configuración del Proyecto

### **Variables de Entorno (.env)**
```env
DB_NAME=crm_ecommerce
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432
DB_SSL=disable
```

### **Instalación**
```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar base de datos
python manage.py makemigrations
python manage.py migrate

# 4. Crear superusuario
python manage.py createsuperuser

# 5. Ejecutar servidor
python manage.py runserver
```

---

## 📖 Documentación Interactiva

- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/
- **Admin Panel**: http://localhost:8000/admin/

---

## 🧪 Testing

### **Endpoints de Prueba**
1. **Health Check**: `GET /api/v1/users/stats/`
2. **Auth Test**: `POST /api/v1/users/login/`
3. **Permission Test**: `GET /api/v1/crm/roles/`

### **Datos de Prueba**
```python
# Crear roles básicos
python manage.py shell
>>> from django.contrib.auth.models import Group
>>> Group.objects.create(name='administrador')
>>> Group.objects.create(name='empleadonivel1')
>>> Group.objects.create(name='empleadonivel2')
>>> Group.objects.create(name='cliente')
```

---

## 🚀 Próximos Pasos (Sprint 2)

1. **Módulo de Ventas**
   - Órdenes de compra
   - Procesamiento de pagos
   - Facturación

2. **Mejoras del Sistema**
   - Notificaciones en tiempo real
   - Reportes avanzados con gráficos
   - Sistema de descuentos y promociones

3. **Interfaces de Usuario**
   - Dashboard administrativo web
   - Portal de clientes
   - Aplicación móvil

---

## 📞 Soporte

Para dudas sobre la implementación:
- Revisar documentación de microconceptos en el código
- Consultar ejemplos en los serializers y views
- Usar Swagger UI para probar endpoints

**¡Sprint 1 Completamente Implementado! 🎉**

### **📋 Resumen Sprint 1:**
- ✅ **4 Módulos**: Users, CRM, Bitácora, E-commerce
- ✅ **25+ Casos de Uso**: Desde CU-01 hasta CU-E13
- ✅ **50+ Endpoints**: API REST completa
- ✅ **Microconceptos**: Documentación educativa integrada
- ✅ **Seguridad**: JWT + Permisos granulares
- ✅ **Auditoría**: Bitácora automática de todas las acciones
