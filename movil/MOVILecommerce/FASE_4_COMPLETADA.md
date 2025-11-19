# Fase 4: Perfil de Usuario e Historial de Pedidos - COMPLETADA ✅

## Resumen de Implementación

La Fase 4 ha sido completada exitosamente. El sistema ahora incluye:

1. **Vista de Perfil**: Información del usuario con avatar, nombre, email y teléfono
2. **Historial de Pedidos**: Lista completa de pedidos con estados, fechas y totales
3. **Estados de Carga**: Shimmer loading para mejor UX
4. **Logout Completo**: Cierre de sesión que limpia JWT y estado de la aplicación

---

## Archivos Implementados

### 1. Modelo Order (Actualizado)
**Archivo**: `lib/data/models/order.dart`

**Métodos helper agregados**:
```dart
String get statusText // Traduce OrderStatus a español
String get formattedDate // Formato DD/MM/YYYY
int get itemCount // Total de items en el pedido
```

**OrderStatus enum**:
- `pending` - Pendiente
- `processing` - Procesando  
- `shipped` - Enviado
- `delivered` - Entregado
- `cancelled` - Cancelado

---

### 2. OrderService (Nuevo)
**Archivo**: `lib/data/repositories/order_service.dart`

**Endpoints implementados**:
- ✅ `GET /orders/history` - Obtener historial de pedidos
- ✅ `GET /orders/:id` - Obtener detalles de un pedido específico
- ✅ `POST /orders` - Crear nuevo pedido (checkout)
- ✅ `PUT /orders/:id/cancel` - Cancelar un pedido

**Método principal**:
```dart
Future<List<Order>> getOrderHistory() async {
  final response = await _apiClient.get('/orders/history');
  // Maneja respuesta como { orders: [...] } o [...]
  return ordersJson.map((json) => Order.fromJson(json)).toList();
}
```

---

### 3. ProfileScreen (Nueva Vista)
**Archivo**: `lib/features/profile/profile_screen.dart`

**Secciones principales**:

#### A. Información del Usuario
- Avatar circular con inicial del nombre
- Nombre completo
- Email
- Teléfono (opcional)
- Botón de editar (placeholder)

#### B. Historial de Pedidos
- **Loading State**: Shimmer skeleton para 3 pedidos
- **Empty State**: "No hay pedidos" con botón para ir a comprar
- **Error State**: Mensaje de error con botón "Reintentar"
- **Lista de Pedidos**: Cards con información completa

#### C. Botón de Logout
- Confirmación con diálogo
- Loading overlay durante el proceso
- Limpieza completa del estado
- Redirección a Home

**Características**:
- ✅ RefreshIndicator para actualizar pedidos
- ✅ Scroll completo con todos los componentes
- ✅ Manejo de usuarios no autenticados
- ✅ Integración con AuthProvider y CartProvider

---

### 4. OrderCard Widget
**Componente**: Incluido en `profile_screen.dart`

**Información mostrada**:
- ID del pedido (primeros 8 caracteres)
- Estado con chip de color:
  - 🟠 Naranja: Pendiente
  - 🔵 Azul: Procesando
  - 🟣 Morado: Enviado
  - 🟢 Verde: Entregado
  - 🔴 Rojo: Cancelado
- Fecha de creación
- Cantidad de artículos
- Número de tracking (si existe)
- Total del pedido

**Interacción**:
- Tap para ver detalles (placeholder implementado)

---

## Flujo de Logout

### Proceso Completo:
1. Usuario presiona "Cerrar Sesión"
2. Aparece diálogo de confirmación
3. Si confirma:
   - Muestra overlay "Cerrando sesión..."
   - Llama a `authProvider.logout()`:
     - Llama a `AuthService.logout()` (limpia JWT del servidor)
     - Limpia token de `flutter_secure_storage`
     - Resetea `_currentUser = null`
     - Resetea `_isAuthenticated = false`
     - Notifica cambios
   - Llama a `cartProvider.clearCart(isAuthenticated: false)`
   - Cierra overlay
   - Navega a Home (`/`)

### Limpieza de Estado:
```dart
await authProvider.logout();  // Limpia JWT y estado de auth
await cartProvider.clearCart(isAuthenticated: false);  // Limpia carrito
context.go('/');  // Navega a home
```

---

## Estados de la Vista

### 1. Usuario No Autenticado
- Muestra prompt para iniciar sesión
- Icono grande de persona
- Texto explicativo
- Botón "Iniciar Sesión" (placeholder)

### 2. Usuario Autenticado - Cargando
- Info de usuario visible
- Shimmer loading en historial de pedidos
- 3 cards skeleton con animación

### 3. Usuario Autenticado - Sin Pedidos
- Info de usuario visible
- Estado vacío con icono de bolsa
- Mensaje: "Aún no has realizado ningún pedido"
- Botón "Ir a Comprar"

### 4. Usuario Autenticado - Con Pedidos
- Info de usuario visible
- Lista completa de pedidos
- Cada pedido como card táctil
- Pull-to-refresh habilitado

### 5. Usuario Autenticado - Error
- Info de usuario visible
- Icono de error
- Mensaje de error descriptivo
- Botón "Reintentar"

---

## Integración con Backend

### Endpoint Principal: GET /orders/history

**Headers requeridos**:
```http
Authorization: Bearer <jwt_token>
```

**Response esperada**:
```json
{
  "orders": [
    {
      "id": "order_123456",
      "userId": "user_123",
      "items": [
        {
          "id": "item_1",
          "product": {
            "id": "prod_123",
            "name": "Producto 1",
            "price": 299.99,
            "imageUrl": "https://..."
          },
          "quantity": 2,
          "price": 299.99
        }
      ],
      "subtotal": 599.98,
      "tax": 95.99,
      "shipping": 0,
      "total": 695.97,
      "status": "delivered",
      "shippingAddress": {
        "street": "Calle Principal 123",
        "city": "Ciudad",
        "state": "Estado",
        "zipCode": "12345"
      },
      "trackingNumber": "TRACK123456",
      "createdAt": "2024-11-15T10:30:00Z",
      "updatedAt": "2024-11-16T14:20:00Z"
    }
  ]
}
```

**O directamente el array**:
```json
[
  { /* order 1 */ },
  { /* order 2 */ }
]
```

**El service maneja ambos formatos** automáticamente.

---

## Testing Manual

### Test 1: Usuario No Autenticado
1. ✅ Hacer logout si estás autenticado
2. ✅ Ir a pestaña "Perfil"
3. ✅ Verificar que aparece el prompt de login
4. ✅ Verificar que no se muestran pedidos

### Test 2: Cargar Historial de Pedidos
1. ✅ Iniciar sesión
2. ✅ Ir a pestaña "Perfil"
3. ✅ Verificar que aparece info del usuario
4. ✅ Verificar shimmer loading
5. ✅ Verificar llamada a `GET /orders/history`
6. ✅ Verificar que se muestran los pedidos (si existen)

### Test 3: Estados de Pedidos
1. ✅ Verificar colores de chips según estado
2. ✅ Verificar textos en español
3. ✅ Verificar formato de fecha
4. ✅ Verificar contador de items

### Test 4: Pull to Refresh
1. ✅ Estando en perfil con pedidos
2. ✅ Hacer pull down
3. ✅ Verificar loading indicator
4. ✅ Verificar nueva llamada a API

### Test 5: Logout Completo
1. ✅ Presionar "Cerrar Sesión"
2. ✅ Confirmar en el diálogo
3. ✅ Verificar overlay "Cerrando sesión..."
4. ✅ Verificar llamada a logout del backend
5. ✅ Verificar redirección a Home
6. ✅ Verificar que el estado está limpio (no autenticado)
7. ✅ Verificar que el carrito está vacío

### Test 6: Estado Vacío
1. ✅ Iniciar sesión con cuenta sin pedidos
2. ✅ Ir a perfil
3. ✅ Verificar mensaje "No hay pedidos"
4. ✅ Presionar "Ir a Comprar"
5. ✅ Verificar navegación a Home

### Test 7: Manejo de Errores
1. ✅ Simular error de red
2. ✅ Verificar estado de error
3. ✅ Presionar "Reintentar"
4. ✅ Verificar nueva llamada a API

---

## Componentes Reutilizables

### SkeletonLoader (Ya existe)
Usado para shimmer loading:
```dart
SkeletonLoader(width: 100, height: 20)
```

### OrderCard
Card táctil para mostrar resumen de pedido:
```dart
OrderCard(
  order: order,
  onTap: () { /* Navegar a detalles */ },
)
```

---

## Próximos Pasos Sugeridos

### Detalles de Pedido (Opcional)
Crear `lib/features/profile/order_detail_screen.dart`:
- Mostrar todos los items del pedido
- Timeline del estado del pedido
- Información completa de envío
- Botón para rastrear envío
- Opción de cancelar (si aplica)

### Editar Perfil (Opcional)
Crear `lib/features/profile/edit_profile_screen.dart`:
- Formulario para editar nombre, teléfono, dirección
- Cambiar contraseña
- Foto de perfil

---

## Archivos Modificados en Esta Fase

1. ✅ `lib/data/models/order.dart` - Agregados métodos helper
2. ✅ `lib/data/repositories/order_service.dart` - Servicio nuevo
3. ✅ `lib/features/profile/profile_screen.dart` - Vista nueva
4. ✅ `lib/main.dart` - Actualizado import y ruta

---

## Endpoints del Backend Requeridos

### 1. GET /orders/history
**Descripción**: Obtener historial de pedidos del usuario

**Headers**: `Authorization: Bearer <token>`

**Query params** (opcionales):
- `limit`: Número de pedidos a retornar
- `offset`: Para paginación
- `status`: Filtrar por estado

**Response**: Ver sección "Integración con Backend"

### 2. GET /orders/:id
**Descripción**: Obtener detalles de un pedido específico

**Headers**: `Authorization: Bearer <token>`

**Response**: Objeto Order completo

### 3. POST /orders
**Descripción**: Crear nuevo pedido (usado en checkout)

**Headers**: `Authorization: Bearer <token>`

**Body**:
```json
{
  "shippingAddress": "string o objeto Address",
  "paymentMethod": "credit_card",
  "notes": "Entregar en la mañana"
}
```

### 4. PUT /orders/:id/cancel
**Descripción**: Cancelar un pedido

**Headers**: `Authorization: Bearer <token>`

**Response**: Order actualizado con status "cancelled"

### 5. POST /auth/logout (Ya implementado en Fase 1)
**Descripción**: Invalidar token en el servidor

**Headers**: `Authorization: Bearer <token>`

---

## Estado del Proyecto

### ✅ Fase 0: Setup Inicial - COMPLETADA
### ✅ Fase 1: Autenticación - COMPLETADA
### ✅ Fase 2: Catálogo de Productos - COMPLETADA
### ✅ Fase 3: Carrito (Anónimo y Sincronizado) - COMPLETADA
### ✅ Fase 4: Perfil de Usuario e Historial de Pedidos - COMPLETADA
### ⏳ Fase 5: Checkout y Órdenes - PENDIENTE (Opcional)
### ⏳ Configuración de la App - PENDIENTE (Settings)

---

## Notas de Implementación

### Shimmer Loading
El shimmer se implementa con `SkeletonLoader` que ya existe en el proyecto.
Simula 3 pedidos mientras carga para mantener la consistencia visual.

### RefreshIndicator
Pull-to-refresh implementado en toda la vista de perfil.
Solo funciona cuando hay scroll disponible (AlwaysScrollableScrollPhysics).

### Gestión de Estado
- Loading, Error y Empty states claramente diferenciados
- Cada estado tiene su UI específica y acciones apropiadas

### Logout Seguro
- Siempre limpia el estado local, incluso si falla la llamada al servidor
- Usa `finally` para garantizar la limpieza
- Muestra feedback visual durante todo el proceso

---

**Fecha de completación**: Noviembre 18, 2025
**Estado**: ✅ FASE 4 COMPLETADA - Lista para integración con backend
