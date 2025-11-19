# E-Commerce Mobile App - Flutter

## 📋 Fase 0: Marco General - Completada ✅

Esta es una aplicación de e-commerce desarrollada en Flutter con arquitectura limpia y buenas prácticas.

## 🏗️ Estructura del Proyecto

```
lib/
├── core/
│   ├── theme/
│   │   └── app_theme.dart          # Temas Material 3 (claro/oscuro)
│   ├── constants/                   # Constantes de la app
│   └── utils/                       # Utilidades generales
│
├── data/
│   ├── models/                      # Modelos de datos
│   │   ├── product.dart
│   │   ├── category.dart
│   │   ├── user.dart
│   │   ├── cart_item.dart
│   │   └── order.dart
│   ├── repositories/                # Repositorios (futura implementación)
│   └── api_client.dart              # Cliente API con Dio + JWT Interceptor
│
├── features/                        # Vistas organizadas por feature
│   ├── home/
│   │   ├── home_view.dart
│   │   └── product_detail_view.dart
│   ├── auth/
│   │   └── auth_view.dart
│   ├── cart/
│   │   └── cart_view.dart
│   ├── profile/
│   │   └── profile_view.dart
│   └── settings/
│       └── settings_view.dart
│
├── providers/                       # State Management (Provider)
│   ├── auth_provider.dart           # Autenticación y usuario
│   ├── cart_provider.dart           # Carrito de compras
│   └── theme_provider.dart          # Modo oscuro/claro
│
├── widgets/                         # Widgets reutilizables
│
└── main.dart                        # Punto de entrada + GoRouter config
```

## 🎯 Características Implementadas

### ✅ 1. Modelos de Datos
Todos los modelos incluyen métodos `fromJson()` y `toJson()`:
- **Product**: Productos con imágenes, precio, stock, ratings
- **Category**: Categorías de productos
- **User**: Usuarios con direcciones
- **CartItem**: Items del carrito
- **Order**: Órdenes con estados (pending, processing, shipped, delivered, cancelled)

### ✅ 2. Cliente API (Dio)
- Singleton pattern para instancia única
- Base URL configurable en `lib/data/api_client.dart`
- **Interceptor JWT**: Añade automáticamente el token Bearer a todas las peticiones
  - Excepciones: `/auth/login` y `/auth/register`
  - Almacenamiento seguro con `flutter_secure_storage`
  - Manejo automático de token expirado (401)
- Logging en desarrollo
- Métodos helper: `get()`, `post()`, `put()`, `delete()`

### ✅ 3. Providers (State Management)

#### AuthProvider
- Login/Register
- Verificación de autenticación
- Gestión de token JWT
- Actualización de perfil
- Logout

#### CartProvider
- Añadir/eliminar productos
- Actualizar cantidades
- Calcular subtotal, impuestos (16%), envío
- Sincronización con backend
- Verificar si producto está en carrito

#### ThemeProvider
- Toggle entre modo claro/oscuro
- Persistencia de preferencia
- Modo sistema

### ✅ 4. Navegación (go_router)

#### Rutas Configuradas:
- `/` - Home (con BottomNavigationBar)
- `/cart` - Carrito (protegida)
- `/profile` - Perfil (protegida)
- `/settings` - Configuración
- `/auth` - Login/Register
- `/product/:id` - Detalle de producto

#### Auth Guard
Rutas protegidas que requieren autenticación:
- `/cart`
- `/checkout`
- `/profile`

Si no está autenticado, redirige automáticamente a `/auth`

### ✅ 5. Temas Material 3
- **Light Theme**: Colores vibrantes, fondo claro
- **Dark Theme**: Colores suaves, fondo oscuro (#121212)
- Componentes personalizados:
  - AppBar
  - Cards
  - Buttons (Elevated, Text, Outlined)
  - Input fields
  - BottomNavigationBar
  - FloatingActionButton

### ✅ 6. AppShell
Contenedor principal con `BottomNavigationBar`:
- Home 🏠
- Carrito 🛒
- Perfil 👤
- Configuración ⚙️

## 🔧 Configuración Inicial

### 1. Configurar URL del Backend

Edita `lib/data/api_client.dart` línea 15:

```dart
baseUrl: 'https://your-api-url.com/api', // ⬅️ Cambia esta URL
```

### 2. Instalar Dependencias

```bash
flutter pub get
```

### 3. Ejecutar la App

```bash
flutter run
```

## 📦 Dependencias Principales

```yaml
dependencies:
  provider: ^6.1.1                    # State management
  go_router: ^13.0.0                  # Navegación declarativa
  dio: ^5.4.0                         # HTTP client
  flutter_secure_storage: ^9.0.0      # Almacenamiento seguro
```

## 🔐 Seguridad

- **JWT Authentication**: Token Bearer automático en headers
- **Secure Storage**: Tokens almacenados con `flutter_secure_storage`
- **Auth Guard**: Rutas protegidas con redirección automática
- **Token Refresh**: Manejo de tokens expirados (401)

## 📱 Características de la App

### Autenticación
- Login con email/password
- Registro de nuevos usuarios
- Persistencia de sesión
- Logout

### Carrito
- Añadir productos con cantidad
- Actualizar cantidades
- Eliminar items
- Cálculo de totales (subtotal + impuestos + envío)
- Envío gratis para órdenes >$500

### Temas
- Modo claro/oscuro
- Persistencia de preferencia
- Toggle manual o automático (sistema)

## 🚀 Próximos Pasos (Fases Siguientes)

1. **Fase 1**: Implementar vistas de autenticación
2. **Fase 2**: Vista Home con listado de productos
3. **Fase 3**: Carrito funcional
4. **Fase 4**: Checkout y órdenes
5. **Fase 5**: Perfil y configuración
6. **Fase 6**: Búsqueda y filtros
7. **Fase 7**: Pulido y optimización

## 📝 Notas Importantes

- Los errores de compilación actuales son normales - desaparecerán después de `flutter pub get`
- Todas las vistas son placeholders - se implementarán en las siguientes fases
- El backend debe seguir la estructura de API esperada por los modelos
- Configura tu `baseUrl` antes de hacer peticiones API

## 🛠️ Comandos Útiles

```bash
# Obtener dependencias
flutter pub get

# Ejecutar en modo debug
flutter run

# Ejecutar en modo release
flutter run --release

# Limpiar build
flutter clean

# Ver paquetes desactualizados
flutter pub outdated

# Actualizar dependencias
flutter pub upgrade


# 1. Iniciar emulador (si no está abierto)
flutter emulators --launch Pixel_7

# 2. Ejecutar la app
flutter run
```

---

**Estado**: ✅ Fase 0 completada - Marco general listo para desarrollo
