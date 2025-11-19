# 🎮 MODO DEMO - Datos Sintéticos

## ✅ Estado Actual

La aplicación ha sido configurada para funcionar en **MODO DEMO** con datos sintéticos y estáticos. No requiere conexión a backend.

## 🔧 Cambios Realizados

### 1. **AuthProvider** (Autenticación)
- ✅ Usuario **siempre autenticado** con datos demo
- ✅ No requiere login real
- ✅ Usuario predefinido:
  - Email: `demo@ejemplo.com`
  - Nombre: `Usuario Demo`

### 2. **ProductProvider** (Productos)
- ✅ 12 productos sintéticos predefinidos
- ✅ 6 categorías: Electrónicos, Ropa, Hogar, Deportes, Libros, Juguetes
- ✅ Búsqueda y filtrado funcionan localmente
- ✅ Productos incluyen:
  - iPhone 15 Pro
  - MacBook Air M3
  - AirPods Pro 2
  - PlayStation 5
  - Robot Aspirador
  - Y más...

### 3. **CartProvider** (Carrito)
- ✅ Carrito vacío al inicio
- ✅ Agregar/eliminar productos funciona localmente
- ✅ Cálculo de totales, impuestos y envío
- ✅ Sin conexión a API

## 🚀 Cómo Ejecutar

```bash
# Desde la raíz del proyecto
flutter run
```

## 📱 Funcionalidades Disponibles

### ✅ Vistas Funcionales
1. **Home** - Listado de productos con búsqueda y filtros
2. **Detalle de Producto** - Información completa del producto
3. **Carrito** - Gestión de items, cantidades y checkout
4. **Perfil** - Vista de usuario (con datos demo)
5. **Configuración** - Tema claro/oscuro

### ✅ Interacciones
- ✅ Buscar productos por nombre/descripción
- ✅ Filtrar por categoría
- ✅ Agregar productos al carrito
- ✅ Modificar cantidades en el carrito
- ✅ Eliminar productos del carrito
- ✅ Ver totales con impuestos y envío
- ✅ Cambiar tema claro/oscuro
- ✅ Navegación completa entre vistas

### ⏱️ Simulación de Carga
- Productos: 800ms
- Categorías: 300ms
- Carrito: 500ms
- Usuario: 500ms
- Operaciones: 200-300ms

## 🔄 Restaurar Conexión a API

Cuando estés listo para conectar al backend real:

1. **AuthProvider**: Revertir el método `initialize()` a usar `AuthService`
2. **ProductProvider**: Revertir métodos a usar `ProductService`
3. **CartProvider**: Revertir métodos a usar `ApiClient`

## 📝 Notas

- Los datos NO se persisten (se pierden al reiniciar la app)
- Perfecto para desarrollo de UI y testing de flujos
- Todas las animaciones y transiciones funcionan normalmente
- Los skeleton loaders se muestran durante las simulaciones de carga

## 🎨 Próximos Pasos

Una vez validadas las vistas, puedes:
1. Ajustar estilos y colores
2. Mejorar animaciones
3. Agregar más productos sintéticos
4. Conectar al backend real
