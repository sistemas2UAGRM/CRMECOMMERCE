import 'package:flutter/foundation.dart';
import '../data/models/carrito_response.dart';
import '../data/models/detalle_pedido.dart';
import '../data/repositories/cart_service.dart';

// SWAGGER-CORRECTED: CartProvider 100% server-side, sin carrito local
class CartProvider extends ChangeNotifier {
  final CartService _cartService = CartService();

  CarritoResponse? _carrito;
  List<DetallePedido> _items = [];
  bool _isLoading = false;
  String? _errorMessage;
  bool _isAuthenticated = false;

  CarritoResponse? get carrito => _carrito;
  List<DetallePedido> get items => _items;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  bool get isAuthenticated => _isAuthenticated;

  int get itemCount => _carrito?.totalItems ?? 0;

  double get subtotal => _carrito?.subtotalDouble ?? 0.0;

  double get tax => subtotal * 0.16; // 16% de impuesto

  double get shipping => subtotal > 500 ? 0 : 50; // Envío gratis si supera $500

  double get total => subtotal + tax + shipping;

  // ========== MÉTODOS PÚBLICOS ==========

  /// Actualizar estado de autenticación
  void setAuthenticated(bool authenticated) {
    _isAuthenticated = authenticated;
    if (!authenticated) {
      // Si el usuario cierra sesión, limpiar el carrito
      _carrito = null;
      _items = [];
      notifyListeners();
    }
  }

  /// Cargar carrito del servidor (solo si está autenticado)
  Future<void> loadCart() async {
    if (!_isAuthenticated) {
      _carrito = null;
      _items = [];
      notifyListeners();
      return;
    }

    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final carritoResponse = await _cartService.getCart();
      _carrito = carritoResponse;
      _items = carritoResponse.items;
      _isLoading = false;
      _errorMessage = null;
      notifyListeners();
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      debugPrint('❌ Error al cargar carrito: $e');
      notifyListeners();
    }
  }

  /// Agregar producto al carrito
  /// SWAGGER-CORRECTED: Requiere autenticación, retorna carrito actualizado
  Future<bool> addToCart(int productId, int quantity) async {
    if (!_isAuthenticated) {
      _errorMessage = 'Debes iniciar sesión para agregar productos al carrito';
      notifyListeners();
      return false;
    }

    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      // El backend retorna el carrito completo actualizado
      final carritoActualizado =
          await _cartService.addToCart(productId, quantity);

      _carrito = carritoActualizado;
      _items = carritoActualizado.items;
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      debugPrint('❌ Error al agregar al carrito: $e');
      notifyListeners();
      return false;
    }
  }

  /// Eliminar un item del carrito
  Future<bool> removeItem(int itemId) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      await _cartService.removeFromCart(itemId);

      // Recargar carrito
      await loadCart();

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      debugPrint('❌ Error al eliminar item: $e');
      notifyListeners();
      return false;
    }
  }

  /// Limpiar mensaje de error
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }

  /// Limpiar carrito (usado después de checkout exitoso)
  void clearCart() {
    _carrito = null;
    _items = [];
    notifyListeners();
  }
}
