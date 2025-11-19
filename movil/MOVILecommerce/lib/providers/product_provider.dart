import 'dart:async';
import 'package:flutter/foundation.dart';
import '../data/models/producto_list.dart';
import '../data/models/producto_detail.dart';
import '../data/repositories/product_service.dart';

/// Provider para gestionar el estado de productos
class ProductProvider extends ChangeNotifier {
  final ProductService _productService = ProductService();

  List<ProductoList> _products = [];
  List<String> _categories = [];
  String? _selectedCategory;
  String _searchQuery = '';
  bool _isLoading = false;
  String? _errorMessage;

  // Paginación
  int _currentPage = 1;
  int _totalCount = 0;
  bool _hasMore = true;

  // Debounce timer para búsqueda
  Timer? _debounceTimer;

  List<ProductoList> get products => _products;
  List<String> get categories => _categories;
  String? get selectedCategory => _selectedCategory;
  String get searchQuery => _searchQuery;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  int get totalCount => _totalCount;
  bool get hasMore => _hasMore;

  /// Inicializar - cargar productos y categorías
  Future<void> initialize() async {
    await loadProducts();
  }

  /// Cargar productos desde el servidor
  Future<void> loadProducts({bool reset = true}) async {
    if (reset) {
      _currentPage = 1;
      _products = [];
      _hasMore = true;
    }

    if (_isLoading || !_hasMore) return;

    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final result = await _productService.getProducts(
        search: _searchQuery.isNotEmpty ? _searchQuery : null,
        page: _currentPage,
      );

      final newProducts = result['productos'] as List<ProductoList>;

      if (reset) {
        _products = newProducts;
      } else {
        _products.addAll(newProducts);
      }

      _totalCount = result['count'] ?? 0;
      _hasMore = result['next'] != null;

      if (_hasMore) {
        _currentPage++;
      }

      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      debugPrint('❌ Error al cargar productos: $e');
      notifyListeners();
    }
  }

  /// Cargar más productos (paginación)
  Future<void> loadMoreProducts() async {
    await loadProducts(reset: false);
  }

  /// Cargar categorías disponibles
  Future<void> loadCategories() async {
    // Extraer categorías únicas de los productos cargados
    final categoriesSet = <String>{};
    for (var product in _products) {
      for (var categoria in product.categorias) {
        categoriesSet.add(categoria.nombre);
      }
    }
    _categories = categoriesSet.toList();
    notifyListeners();
  }

  /// Cambiar categoría seleccionada
  Future<void> setCategory(String? category) async {
    if (_selectedCategory != category) {
      _selectedCategory = category;
      notifyListeners();
      await loadProducts();
    }
  }

  /// Actualizar query de búsqueda con debounce
  void setSearchQuery(String query) {
    _searchQuery = query;
    notifyListeners();

    // Cancelar timer anterior si existe
    _debounceTimer?.cancel();

    // Crear nuevo timer de 500ms
    _debounceTimer = Timer(const Duration(milliseconds: 500), () {
      loadProducts(reset: true);
    });
  }

  /// Limpiar búsqueda
  Future<void> clearSearch() async {
    _searchQuery = '';
    notifyListeners();
    await loadProducts(reset: true);
  }

  /// Limpiar filtros (categoría y búsqueda)
  Future<void> clearFilters() async {
    _selectedCategory = null;
    _searchQuery = '';
    notifyListeners();
    await loadProducts(reset: true);
  }

  /// Recargar productos (pull to refresh)
  Future<void> refresh() async {
    await loadProducts(reset: true);
  }

  /// Obtener un producto por ID desde el servidor
  Future<ProductoDetail> getProductById(String id) async {
    try {
      return await _productService.getProductById(int.parse(id));
    } catch (e) {
      _errorMessage = 'Producto no encontrado';
      notifyListeners();
      rethrow;
    }
  }

  /// Limpiar mensaje de error
  void clearError() {
    _errorMessage = null;
    notifyListeners();
  }

  @override
  void dispose() {
    _debounceTimer?.cancel();
    super.dispose();
  }
}
