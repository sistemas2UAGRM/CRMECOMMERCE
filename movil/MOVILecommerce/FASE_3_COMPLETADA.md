# Fase 3: Carrito (Anónimo y Sincronizado) - COMPLETADA ✅

## Resumen de Implementación

La Fase 3 ha sido completada exitosamente. El sistema de carrito ahora soporta:

1. **Carrito Anónimo**: Los usuarios no autenticados pueden agregar productos y se guardan en `shared_preferences`
2. **Carrito Autenticado**: Los usuarios autenticados sincronizan con el backend
3. **Sincronización Automática**: Al hacer login, el carrito local se fusiona con el del servidor

---

## Archivos Implementados

### 1. CartProvider (Actualizado)
**Archivo**: `lib/providers/cart_provider.dart`

**Funcionalidades principales**:
- ✅ Guarda el carrito localmente en `shared_preferences` (usuarios anónimos)
- ✅ Método `loadCart(isAuthenticated)` que carga del servidor o local según el estado
- ✅ Método `addItem()` que requiere parámetro `isAuthenticated`
- ✅ Método `syncWithServer()` que fusiona el carrito local con el servidor
- ✅ Métodos `updateQuantity()` y `removeItem()` con soporte para ambos modos

**Métodos clave**:
```dart
// Cargar carrito (local o servidor)
await cartProvider.loadCart(isAuthenticated: authProvider.isAuthenticated);

// Agregar item
await cartProvider.addItem(
  product,
  quantity: 1,
  isAuthenticated: authProvider.isAuthenticated,
);

// Sincronizar después del login
await cartProvider.syncWithServer();
```

---

### 2. CartService (Nuevo)
**Archivo**: `lib/data/repositories/cart_service.dart`

**Endpoints implementados**:
- ✅ `GET /cart` - Obtener carrito del servidor
- ✅ `POST /cart` - Añadir producto al carrito
- ✅ `POST /cart/merge` - Fusionar carrito local con el del servidor (CRÍTICO)
- ✅ `PUT /cart/:id` - Actualizar cantidad de un item
- ✅ `DELETE /cart/:id` - Eliminar item del carrito
- ✅ `DELETE /cart` - Limpiar todo el carrito

**Método de merge**:
```dart
Future<void> mergeLocalCart(List<CartItem> localItems) async {
  final itemsToMerge = localItems.map((item) => {
    'productId': item.product.id,
    'quantity': item.quantity,
  }).toList();

  await _apiClient.post('/cart/merge', data: {'items': itemsToMerge});
}
```

---

### 3. CartScreen (Nueva Vista)
**Archivo**: `lib/features/cart/cart_screen.dart`

**Características**:
- ✅ Modal de login para usuarios anónimos
- ✅ Lista de items con `Dismissible` para eliminar
- ✅ Controles de cantidad (+/-)
- ✅ Resumen con subtotal, IVA (16%), envío y total
- ✅ Estado vacío cuando no hay items
- ✅ Botón de "Limpiar carrito"
- ✅ Integración completa con `CartProvider` y `AuthProvider`

**UI Components**:
- `CartItemCard` - Tarjeta de producto con imagen, nombre, precio, cantidad
- `CartSummary` - Resumen de costos y botón de checkout
- `QuantityButton` - Botones para incrementar/decrementar cantidad
- `SummaryRow` - Fila de resumen (subtotal, IVA, etc.)

---

### 4. AuthProvider (Actualizado)
**Archivo**: `lib/providers/auth_provider.dart`

**Cambios**:
- ✅ Inicialización revisada para verificar token guardado
- ✅ Ya no está en "modo demo" (inicia como no autenticado)
- ✅ Comentarios documentando la necesidad de sincronizar el carrito después del login

**Comentario importante en el código**:
```dart
// Login
// IMPORTANTE: Después de un login exitoso, el UI debe llamar a
// CartProvider.syncWithServer() para sincronizar el carrito local
```

---

## Flujo de Sincronización (CRÍTICO)

### Escenario 1: Usuario Anónimo Agrega Items
1. Usuario navega y agrega productos al carrito
2. `CartProvider.addItem()` detecta que `isAuthenticated = false`
3. Items se guardan localmente en `shared_preferences`
4. El carrito persiste entre sesiones de la app

### Escenario 2: Usuario Inicia Sesión con Carrito Local
1. Usuario con items en carrito local hace login
2. UI debe llamar a `CartProvider.syncWithServer()` (ver nota abajo)
3. Proceso de sincronización:
   - Lee items de `shared_preferences`
   - Si hay items, muestra overlay "Sincronizando carrito..."
   - Llama a `CartService.mergeLocalCart(localItems)`
   - Backend fusiona (suma cantidades, evita duplicados)
   - Borra carrito local de `shared_preferences`
   - Obtiene carrito actualizado del servidor con `getCart()`
   - Actualiza UI con carrito sincronizado

### Escenario 3: Usuario Autenticado Agrega Items
1. Usuario autenticado agrega producto
2. `CartProvider.addItem()` detecta que `isAuthenticated = true`
3. Envía request `POST /cart` al servidor
4. Obtiene carrito actualizado del servidor
5. Actualiza UI

---

## Integración con LoginScreen (TODO)

Cuando se implemente el `LoginScreen`, agregar este código después de un login exitoso:

```dart
// En LoginScreen después de login exitoso
final authProvider = context.read<AuthProvider>();
final cartProvider = context.read<CartProvider>();

final success = await authProvider.login(email, password);

if (success) {
  // Mostrar overlay de sincronización
  showDialog(
    context: context,
    barrierDismissible: false,
    builder: (context) => const Center(
      child: Card(
        child: Padding(
          padding: EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              CircularProgressIndicator(),
              SizedBox(height: 16),
              Text('Sincronizando carrito...'),
            ],
          ),
        ),
      ),
    ),
  );

  try {
    // Sincronizar carrito
    await cartProvider.syncWithServer();
    
    // Cerrar overlay
    Navigator.pop(context);
    
    // Navegar a home o donde corresponda
    context.go('/');
  } catch (e) {
    // Cerrar overlay
    Navigator.pop(context);
    
    // Mostrar error pero continuar (el login fue exitoso)
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Error al sincronizar carrito: $e')),
    );
    
    context.go('/');
  }
}
```

---

## Dependencias Agregadas

**pubspec.yaml**:
```yaml
dependencies:
  shared_preferences: ^2.2.2  # Para carrito anónimo
```

Ejecutar:
```bash
flutter pub get
```

---

## Testing Manual

### Test 1: Carrito Anónimo
1. ✅ Cerrar sesión (si estás autenticado)
2. ✅ Agregar productos al carrito
3. ✅ Cerrar y reabrir la app
4. ✅ Verificar que los items persisten

### Test 2: Modal de Login
1. ✅ Estando como anónimo, ir a la pestaña "Carrito"
2. ✅ Verificar que aparece el modal pidiendo iniciar sesión
3. ✅ Verificar botones de "Iniciar Sesión" y "Crear Cuenta"

### Test 3: Sincronización (Requiere Backend)
1. ✅ Como anónimo, agregar items al carrito
2. ✅ Iniciar sesión
3. ✅ Verificar llamada a `POST /cart/merge` en logs
4. ✅ Verificar que el carrito sincronizado aparece correctamente

### Test 4: Carrito Autenticado
1. ✅ Estando autenticado, agregar items
2. ✅ Verificar llamada a `POST /cart` en logs
3. ✅ Ir a la vista de carrito
4. ✅ Verificar llamada a `GET /cart` al cargar

### Test 5: Operaciones en Carrito
1. ✅ Incrementar/decrementar cantidad con botones +/-
2. ✅ Eliminar item con swipe (Dismissible)
3. ✅ Limpiar carrito completo
4. ✅ Verificar cálculos de subtotal, IVA, envío y total

---

## Endpoints del Backend Requeridos

El backend debe implementar estos endpoints:

### 1. GET /cart
**Descripción**: Obtener carrito del usuario autenticado

**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
{
  "items": [
    {
      "id": "cart_item_id",
      "product": { ... },
      "quantity": 2,
      "price": 299.99
    }
  ]
}
```

### 2. POST /cart
**Descripción**: Añadir producto al carrito

**Headers**: `Authorization: Bearer <token>`

**Body**:
```json
{
  "productId": "product_123",
  "quantity": 1
}
```

### 3. POST /cart/merge (CRÍTICO)
**Descripción**: Fusionar carrito local con el del servidor

**Headers**: `Authorization: Bearer <token>`

**Body**:
```json
{
  "items": [
    { "productId": "product_123", "quantity": 2 },
    { "productId": "product_456", "quantity": 1 }
  ]
}
```

**Lógica del backend**:
- Para cada item del carrito local:
  - Si el producto ya existe en el carrito del servidor, SUMAR las cantidades
  - Si no existe, agregarlo como nuevo item
- Retornar el carrito fusionado

### 4. PUT /cart/:itemId
**Descripción**: Actualizar cantidad de un item

**Body**:
```json
{
  "quantity": 5
}
```

### 5. DELETE /cart/:itemId
**Descripción**: Eliminar un item del carrito

### 6. DELETE /cart
**Descripción**: Limpiar todo el carrito

---

## Notas Importantes

### Shared Preferences
- Los datos se guardan como JSON string
- Key utilizada: `'local_cart'`
- Se borra automáticamente después de sincronizar con el servidor

### Estados del Carrito
1. **Anónimo**: Solo en `shared_preferences`, sin llamadas al servidor
2. **Autenticado**: Solo en el servidor, sin `shared_preferences`
3. **Transición (login)**: Merge de ambos y limpieza de local

### Cálculos
- **IVA**: 16% del subtotal
- **Envío**: GRATIS si subtotal > $500, sino $50
- **Total**: subtotal + IVA + envío

---

## Próximos Pasos

### Fase 4: Perfil y Configuraciones (Pendiente)
- Vista de perfil de usuario
- Editar información personal
- Historial de pedidos
- Configuración de notificaciones
- Cambio de tema claro/oscuro

### Fase 5: Checkout y Órdenes (Pendiente)
- Formulario de dirección de envío
- Selección de método de pago
- Confirmación de orden
- Integración con pasarela de pagos
- Seguimiento de pedidos

---

## Archivos Modificados en Esta Fase

1. ✅ `lib/providers/cart_provider.dart` - Lógica completa de carrito
2. ✅ `lib/data/repositories/cart_service.dart` - Servicio de API
3. ✅ `lib/features/cart/cart_screen.dart` - Vista de carrito
4. ✅ `lib/providers/auth_provider.dart` - Inicialización actualizada
5. ✅ `lib/data/repositories/auth_service.dart` - Método getStoredToken()
6. ✅ `lib/main.dart` - Actualizar import de CartScreen
7. ✅ `lib/features/home/product_detail_view.dart` - Actualizar addItem()
8. ✅ `pubspec.yaml` - Agregar shared_preferences

---

## Estado del Proyecto

### ✅ Fase 0: Setup Inicial - COMPLETADA
### ✅ Fase 1: Autenticación - COMPLETADA
### ✅ Fase 2: Catálogo de Productos - COMPLETADA
### ✅ Fase 3: Carrito (Anónimo y Sincronizado) - COMPLETADA
### ⏳ Fase 4: Perfil y Configuraciones - PENDIENTE
### ⏳ Fase 5: Checkout y Órdenes - PENDIENTE

---

**Fecha de completación**: Noviembre 18, 2025
**Estado**: ✅ FASE 3 COMPLETADA - Lista para integración con backend
