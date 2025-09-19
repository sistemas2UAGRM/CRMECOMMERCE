# 📋 ANÁLISIS COMPLETO DE CASOS DE USO - BACKEND DJANGO

## 🎯 RESUMEN EJECUTIVO

El Backend implementa **4 módulos principales** con casos de uso específicos que cubren las funcionalidades de un sistema CRM+E-commerce completo.

---

## 📊 CASOS DE USO IDENTIFICADOS POR MÓDULO

### 🔐 **MÓDULO USUARIOS** (User Management)
**Archivos**: `api/v1/users/views.py`, `api/v1/users/serializers.py`

#### CU-U01: Registro Público de Clientes
- **Endpoint**: `POST /api/v1/users/register/`
- **Descripción**: Cualquier persona puede registrarse como cliente
- **Validaciones**: Email único, confirmación de contraseña, términos y condiciones
- **Rol asignado**: `cliente` automáticamente
- **Estado**: ✅ **IMPLEMENTADO**

#### CU-U02: Registro de Usuarios por Administrador
- **Endpoint**: `POST /api/v1/users/admin-register/`
- **Descripción**: Administradores crean usuarios con roles específicos
- **Roles disponibles**: `administrador`, `empleadonivel1`, `empleadonivel2`, `cliente`
- **Características**: Contraseña generada automáticamente, email de bienvenida
- **Estado**: ✅ **IMPLEMENTADO**

#### CU-U03: Autenticación con JWT
- **Endpoint**: `POST /api/v1/users/login/`
- **Descripción**: Login con email/contraseña que retorna tokens JWT
- **Tokens**: Access token (1 hora) + Refresh token (30 días)
- **Estado**: ✅ **IMPLEMENTADO**

#### CU-U04: Gestión de Perfil de Usuario
- **Endpoints**: 
  - `GET /api/v1/users/profile/` - Ver perfil
  - `PUT/PATCH /api/v1/users/profile/` - Actualizar perfil
- **Descripción**: Usuario puede ver y actualizar su información personal
- **Estado**: ✅ **IMPLEMENTADO**

#### CU-U05: Búsqueda de Usuarios
- **Endpoint**: `GET /api/v1/users/search/?q=juan`
- **Descripción**: Buscar usuarios por username, email, nombre o apellido
- **Permisos**: Solo administradores y supervisores
- **Estado**: ✅ **IMPLEMENTADO**

#### CU-U06: Listar Usuarios Activos
- **Endpoint**: `GET /api/v1/users/active/`
- **Descripción**: Obtener solo usuarios con is_active=True
- **Estado**: ✅ **IMPLEMENTADO**

#### CU-U07: Usuarios por Rol
- **Endpoint**: `GET /api/v1/users/by-role/{role_name}/`
- **Descripción**: Filtrar usuarios por rol específico
- **Estado**: ✅ **IMPLEMENTADO**

#### CU-U08: Estadísticas de Usuarios
- **Endpoint**: `GET /api/v1/users/stats/`
- **Descripción**: Métricas como total usuarios, usuarios por rol, usuarios activos
- **Estado**: ✅ **IMPLEMENTADO**

---

### 🔐 **MÓDULO CRM** (Roles y Permisos)
**Archivos**: `api/v1/crm/views.py`, `api/v1/crm/serializers.py`

#### CU-C01: Gestión de Roles (CRUD)
- **Endpoints**: 
  - `GET /api/v1/crm/roles/` - Listar roles
  - `POST /api/v1/crm/roles/` - Crear rol
  - `GET /api/v1/crm/roles/{id}/` - Detalle de rol
  - `PUT /api/v1/crm/roles/{id}/` - Actualizar rol
- **Descripción**: Administración completa de roles del sistema
- **Estado**: ✅ **IMPLEMENTADO**

#### CU-C02: Gestión de Permisos de Rol
- **Endpoints**:
  - `GET /api/v1/crm/roles/{id}/permissions/` - Ver permisos de rol
  - `PUT /api/v1/crm/roles/{id}/permissions/` - Actualizar permisos
- **Descripción**: Asignar/remover permisos específicos a roles
- **Estado**: ✅ **IMPLEMENTADO**

#### CU-C03: Asignación de Roles a Usuario
- **Endpoint**: `POST /api/v1/crm/assign-role/{user_id}/`
- **Descripción**: Asignar múltiples roles a un usuario específico
- **Auditoría**: Registra motivo de asignación en bitácora
- **Estado**: ✅ **IMPLEMENTADO**

#### CU-C04: Consultar Usuarios por Rol
- **Endpoint**: `GET /api/v1/crm/users-by-role/{role_name}/`
- **Descripción**: Ver qué usuarios tienen un rol específico
- **Estado**: ✅ **IMPLEMENTADO**

#### CU-C05: Listar Permisos Disponibles
- **Endpoint**: `GET /api/v1/crm/permisos/`
- **Descripción**: Ver todos los permisos disponibles en el sistema
- **Estado**: ✅ **IMPLEMENTADO**

---

### 📊 **MÓDULO AUDITORÍA** (Bitácora)
**Archivos**: `api/v1/common/views.py`, `api/v1/common/serializers.py`

#### CU-A01: Consultar Bitácora
- **Endpoint**: `GET /api/v1/common/bitacora/`
- **Descripción**: Ver registro de todas las acciones del sistema
- **Filtros**: Por fecha, usuario, acción, IP
- **Permisos jerárquicos**: Administradores ven todo, supervisores su equipo, vendedores solo sus acciones
- **Estado**: ✅ **IMPLEMENTADO**

#### CU-A02: Estadísticas de Auditoría
- **Endpoint**: `GET /api/v1/common/bitacora/stats/`
- **Descripción**: Métricas como acciones por día, usuarios activos, tipos de acciones
- **Estado**: ✅ **IMPLEMENTADO**

#### CU-A03: Exportar Registros de Auditoría
- **Endpoint**: `GET /api/v1/common/bitacora/export/`
- **Descripción**: Exportar registros filtrados (máximo 10,000)
- **Permisos**: Solo administradores
- **Estado**: ✅ **IMPLEMENTADO**

#### CU-A04: Registro Automático de Acciones
- **Descripción**: Todas las acciones importantes se registran automáticamente
- **Datos**: Usuario, acción, fecha/hora, IP, detalles
- **Estado**: ✅ **IMPLEMENTADO**

---

### 🛍️ **MÓDULO E-COMMERCE** (Productos y Carritos)
**Archivos**: `api/v1/ecommerce/views.py`, `api/v1/ecommerce/serializers.py`

#### **GESTIÓN DE CATEGORÍAS**

#### CU-E01: Gestión de Categorías (CRUD)
- **Endpoints**:
  - `GET /api/v1/ecommerce/categorias/` - Listar categorías
  - `POST /api/v1/ecommerce/categorias/` - Crear categoría
  - `GET /api/v1/ecommerce/categorias/{id}/` - Detalle de categoría
- **Descripción**: Administración de categorías de productos
- **Estado**: ✅ **IMPLEMENTADO**

#### **GESTIÓN DE PRODUCTOS**

#### CU-E02: Crear Producto
- **Endpoint**: `POST /api/v1/ecommerce/productos/`
- **Descripción**: Crear nuevo producto con stock inicial
- **Validaciones**: Precio positivo, stock válido, categoría existente
- **Estado**: ✅ **IMPLEMENTADO**

#### CU-E03: Listar Catálogo de Productos
- **Endpoint**: `GET /api/v1/ecommerce/productos/`
- **Descripción**: Ver catálogo público de productos activos
- **Filtros**: Por categoría, precio, disponibilidad
- **Estado**: ✅ **IMPLEMENTADO**

#### CU-E04: Detalle de Producto
- **Endpoint**: `GET /api/v1/ecommerce/productos/{id}/`
- **Descripción**: Ver información completa de un producto
- **Estado**: ✅ **IMPLEMENTADO**

#### CU-E05: Actualizar Stock de Producto
- **Endpoint**: `PUT /api/v1/ecommerce/productos/{id}/stock/`
- **Descripción**: Actualizar cantidad en stock (solo admin/supervisor)
- **Validaciones**: Stock no negativo
- **Estado**: ✅ **IMPLEMENTADO**

#### **GESTIÓN DE CARRITOS**

#### CU-E06: Crear Carrito
- **Descripción**: Se crea automáticamente cuando usuario agrega primer producto
- **Estado**: ✅ **IMPLEMENTADO**

#### CU-E07: Agregar Producto al Carrito
- **Endpoint**: `POST /api/v1/ecommerce/carritos/{id}/productos/`
- **Descripción**: Agregar producto con cantidad específica
- **Validaciones**: Stock disponible, producto activo
- **Estado**: ✅ **IMPLEMENTADO**

#### CU-E08: Ver Mi Carrito
- **Endpoint**: `GET /api/v1/ecommerce/carritos/mi-carrito/`
- **Descripción**: Ver carrito actual del usuario autenticado
- **Información**: Productos, cantidades, subtotales, total
- **Estado**: ✅ **IMPLEMENTADO**

#### CU-E09: Actualizar Cantidad en Carrito
- **Endpoint**: `PUT /api/v1/ecommerce/carritos/{id}/productos/{producto_id}/`
- **Descripción**: Cambiar cantidad de un producto en el carrito
- **Estado**: ✅ **IMPLEMENTADO**

#### CU-E10: Eliminar Producto del Carrito
- **Endpoint**: `DELETE /api/v1/ecommerce/carritos/{id}/productos/{producto_id}/`
- **Descripción**: Remover producto completamente del carrito
- **Estado**: ✅ **IMPLEMENTADO**

#### **REPORTES Y ESTADÍSTICAS**

#### CU-E11: Estadísticas de Productos
- **Endpoint**: `GET /api/v1/ecommerce/productos/stats/`
- **Descripción**: Métricas como total productos, por categoría, stock bajo
- **Estado**: ✅ **IMPLEMENTADO**

#### CU-E12: Productos por Categoría
- **Endpoint**: `GET /api/v1/ecommerce/categorias/{id}/productos/`
- **Descripción**: Listar productos de una categoría específica
- **Estado**: ✅ **IMPLEMENTADO**

#### CU-E13: Filtrar Productos por Estado
- **Endpoint**: `GET /api/v1/ecommerce/productos/por-estado/?estado={disponible|agotado|no_disponible}`
- **Descripción**: Filtrar productos según disponibilidad
- **Estados**: 
  - `disponible`: activo=True y stock > 0
  - `agotado`: activo=True y stock = 0
  - `no_disponible`: activo=False
- **Estado**: ✅ **IMPLEMENTADO**

---

## 🎯 **ANÁLISIS DE COMPLEJIDAD**

### ⚠️ **ARCHIVOS QUE NECESITAN SIMPLIFICACIÓN**

#### 1. **`api/v1/users/views.py`** (797 líneas)
**Problemas identificados:**
- Una sola clase `UserViewSet` con demasiadas responsabilidades
- Múltiples decoradores Swagger muy largos (50+ líneas cada uno)
- Lógica de permisos repetida en múltiples métodos
- Métodos muy largos (algunos 50+ líneas)

**Soluciones propuestas:**
- Separar en múltiples ViewSets especializados
- Crear mixins para lógica de permisos común
- Simplificar documentación Swagger
- Extraer validaciones a métodos auxiliares

#### 2. **`api/v1/common/views.py`** (341 líneas)
**Problemas identificados:**
- Método `apply_custom_filters()` muy largo (50+ líneas)
- Lógica de estadísticas compleja en `stats()`
- Múltiples validaciones anidadas

**Soluciones propuestas:**
- Crear clases Filter separadas
- Extraer cálculo de estadísticas a servicios
- Usar django-filter para filtros complejos

#### 3. **`api/v1/crm/views.py`** (345 líneas)
**Problemas identificados:**
- Similar al módulo users, muchas responsabilidades en pocas clases
- Lógica de auditoría duplicada

**Soluciones propuestas:**
- Crear decorador para auditoría automática
- Separar gestión de roles de gestión de permisos

#### 4. **`api/v1/ecommerce/views.py`** (568 líneas)
**Problemas identificados:**
- El archivo más largo, maneja categorías, productos y carritos
- Cálculos complejos de totales en múltiples lugares
- Validaciones de stock duplicadas

**Soluciones propuestas:**
- Separar en 3 archivos: categorias_views.py, productos_views.py, carritos_views.py
- Crear servicio para cálculos de carrito
- Crear validadores reutilizables para stock

---

## 🔧 **RECOMENDACIONES DE REFACTORING**

### 📁 **Estructura Propuesta**
```
api/v1/
├── users/
│   ├── views/
│   │   ├── __init__.py
│   │   ├── auth_views.py          # Login, registro
│   │   ├── profile_views.py       # Gestión de perfil
│   │   ├── admin_views.py         # Administración de usuarios
│   │   └── search_views.py        # Búsquedas y estadísticas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py        # Lógica de autenticación
│   │   └── user_service.py        # Lógica de negocio usuarios
│   └── mixins/
│       ├── __init__.py
│       └── permissions_mixin.py   # Permisos reutilizables
├── crm/
│   ├── views/
│   │   ├── roles_views.py
│   │   └── permissions_views.py
│   └── services/
│       └── role_assignment_service.py
├── ecommerce/
│   ├── views/
│   │   ├── categorias_views.py
│   │   ├── productos_views.py
│   │   └── carritos_views.py
│   └── services/
│       ├── cart_service.py        # Lógica de carrito
│       └── stock_service.py       # Gestión de inventario
└── common/
    ├── mixins/
    │   ├── audit_mixin.py         # Auditoría automática
    │   └── pagination_mixin.py    # Paginación consistente
    └── services/
        └── audit_service.py       # Servicio de bitácora
```

### 🎯 **Beneficios del Refactoring**
1. **Mantenibilidad**: Archivos más pequeños y enfocados
2. **Reutilización**: Servicios y mixins compartidos
3. **Testabilidad**: Cada componente se puede testear independientemente
4. **Escalabilidad**: Fácil agregar nuevas funcionalidades
5. **Legibilidad**: Código más fácil de entender y modificar

---

## ✅ **ESTADO ACTUAL: SPRINT 1 COMPLETO**

### 📊 **Métricas de Implementación**
- **Total Casos de Uso**: **25+ casos** implementados
- **Endpoints API**: **50+ endpoints** funcionales
- **Cobertura**: **100%** de los casos de uso del Sprint 1
- **Documentación**: API completamente documentada con Swagger

### 🚀 **Funcionalidades Principales Operativas**
1. ✅ Sistema de autenticación JWT completo
2. ✅ Gestión de usuarios con roles jerárquicos
3. ✅ Auditoría completa de acciones
4. ✅ Catálogo de productos funcional
5. ✅ Sistema de carritos de compra
6. ✅ API REST totalmente documentada

### 📈 **Preparado para Sprint 2**
- Estructura sólida para agregar funcionalidades de ventas
- Base de datos optimizada para transacciones
- Sistema de permisos escalable
- Auditoría completa para cumplimiento

---

**💡 El backend está completamente funcional y cumple con todos los requisitos del Sprint 1, pero se beneficiaría significativamente de un refactoring para mejorar la mantenibilidad a largo plazo.**
