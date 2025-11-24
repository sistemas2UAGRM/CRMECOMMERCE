import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/product_provider.dart';
import '../../providers/tenant_provider.dart';
import '../../data/models/producto_list.dart';
import '../../widgets/skeleton_loader.dart';
import '../../widgets/empty_state.dart';
import '../auth/auth_view.dart';

class HomeView extends StatefulWidget {
  const HomeView({super.key});

  @override
  State<HomeView> createState() => _HomeViewState();
}

class _HomeViewState extends State<HomeView> {
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    // Cargar productos al iniciar
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ProductProvider>().initialize();
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();
    final productProvider = context.watch<ProductProvider>();
    final tenantProvider = context.watch<TenantProvider>();

    return Scaffold(
      appBar: AppBar(
        title: Text(tenantProvider.currentTenant?.name ?? 'E-commerce'),
        actions: [
          // MULTI-TENANT: Botón para cambiar de tienda
          IconButton(
            icon: const Icon(Icons.store),
            tooltip: 'Cambiar tienda',
            onPressed: () {
              showDialog(
                context: context,
                builder: (context) => AlertDialog(
                  title: const Text('Cambiar de tienda'),
                  content: Text(
                    '¿Deseas salir de "${tenantProvider.currentTenant?.name}" y seleccionar otra tienda?',
                  ),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(context),
                      child: const Text('Cancelar'),
                    ),
                    FilledButton(
                      onPressed: () async {
                        // Limpiar tenant y auth
                        await tenantProvider.clearTenant();
                        await authProvider.logout();
                        if (context.mounted) {
                          Navigator.pop(context);
                          context.go('/tenant-selection');
                        }
                      },
                      child: const Text('Cambiar'),
                    ),
                  ],
                ),
              );
            },
          ),
          // Botón de autenticación
          if (!authProvider.isAuthenticated)
            TextButton.icon(
              onPressed: () {
                AuthView.show(context);
              },
              icon: const Icon(Icons.login, color: Colors.white),
              label: const Text(
                'Iniciar Sesión',
                style: TextStyle(color: Colors.white),
              ),
            )
          else
            PopupMenuButton<String>(
              icon: const Icon(Icons.account_circle),
              onSelected: (value) async {
                if (value == 'logout' && mounted) {
                  await authProvider.logout();
                  if (mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Sesión cerrada exitosamente'),
                        backgroundColor: Colors.green,
                      ),
                    );
                  }
                }
              },
              itemBuilder: (BuildContext context) => [
                PopupMenuItem(
                  enabled: false,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        authProvider.currentUser?.fullName ?? 'Usuario',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      Text(
                        authProvider.currentUser?.email ?? '',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ),
                const PopupMenuDivider(),
                const PopupMenuItem(
                  value: 'logout',
                  child: Row(
                    children: [
                      Icon(Icons.logout, size: 20),
                      SizedBox(width: 8),
                      Text('Cerrar Sesión'),
                    ],
                  ),
                ),
              ],
            ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => productProvider.refresh(),
        child: Column(
          children: [
            // Barra de búsqueda
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: TextField(
                controller: _searchController,
                decoration: InputDecoration(
                  hintText: 'Buscar productos...',
                  prefixIcon: const Icon(Icons.search),
                  suffixIcon: _searchController.text.isNotEmpty
                      ? IconButton(
                          icon: const Icon(Icons.clear),
                          onPressed: () {
                            _searchController.clear();
                            productProvider.clearSearch();
                          },
                        )
                      : null,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  filled: true,
                  fillColor: Colors.grey[100],
                ),
                onChanged: (value) {
                  productProvider.setSearchQuery(value);
                },
              ),
            ),

            // Filtro de categorías
            if (productProvider.categories.isNotEmpty)
              SizedBox(
                height: 50,
                child: ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  scrollDirection: Axis.horizontal,
                  itemCount: productProvider.categories.length + 1,
                  itemBuilder: (context, index) {
                    if (index == 0) {
                      // Opción "Todos"
                      return Padding(
                        padding: const EdgeInsets.only(right: 8),
                        child: FilterChip(
                          label: const Text('Todos'),
                          selected: productProvider.selectedCategory == null,
                          onSelected: (_) {
                            productProvider.setCategory(null);
                          },
                        ),
                      );
                    }

                    final category = productProvider.categories[index - 1];
                    return Padding(
                      padding: const EdgeInsets.only(right: 8),
                      child: FilterChip(
                        label: Text(_formatCategoryName(category)),
                        selected: productProvider.selectedCategory == category,
                        onSelected: (_) {
                          productProvider.setCategory(category);
                        },
                      ),
                    );
                  },
                ),
              ),

            const SizedBox(height: 8),

            // Contenido principal
            Expanded(
              child: _buildProductGrid(productProvider),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProductGrid(ProductProvider productProvider) {
    // Estado de carga
    if (productProvider.isLoading) {
      return const ProductGridSkeleton();
    }

    // Estado de error
    if (productProvider.errorMessage != null) {
      return ErrorState(
        errorMessage: productProvider.errorMessage,
        onRetry: () => productProvider.loadProducts(),
      );
    }

    // Estado vacío
    if (productProvider.products.isEmpty) {
      return NoProductsFound(
        onClearFilters: () => productProvider.clearFilters(),
      );
    }

    // Grid de productos
    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        childAspectRatio: 0.7,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
      ),
      itemCount: productProvider.products.length,
      itemBuilder: (context, index) {
        final product = productProvider.products[index];
        return _ProductCard(product: product);
      },
    );
  }

  String _formatCategoryName(String category) {
    return category[0].toUpperCase() + category.substring(1);
  }
}

/// Tarjeta de producto individual
class _ProductCard extends StatelessWidget {
  final ProductoList product;

  const _ProductCard({required this.product});

  @override
  Widget build(BuildContext context) {
    return Hero(
      tag: 'product-${product.id}',
      child: Card(
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        child: InkWell(
          onTap: () {
            context.push('/product/${product.id}');
          },
          borderRadius: BorderRadius.circular(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Imagen del producto
              Expanded(
                child: ClipRRect(
                  borderRadius: const BorderRadius.vertical(
                    top: Radius.circular(12),
                  ),
                  child: Stack(
                    children: [
                      // Imagen
                      Image.network(
                        product.imagenPrincipalUrl ?? '',
                        width: double.infinity,
                        fit: BoxFit.cover,
                        errorBuilder: (context, error, stackTrace) {
                          return Container(
                            color: Colors.grey[200],
                            child: const Center(
                              child: Icon(
                                Icons.image_not_supported,
                                size: 50,
                                color: Colors.grey,
                              ),
                            ),
                          );
                        },
                        loadingBuilder: (context, child, loadingProgress) {
                          if (loadingProgress == null) return child;
                          return Container(
                            color: Colors.grey[200],
                            child: const Center(
                              child: CircularProgressIndicator(),
                            ),
                          );
                        },
                      ),
                      // Badge de stock bajo
                      if (product.stockTotal != null &&
                          product.stockTotal! < 5 &&
                          product.stockTotal! > 0)
                        Positioned(
                          top: 8,
                          right: 8,
                          child: Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 4,
                            ),
                            decoration: BoxDecoration(
                              color: Colors.orange,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Text(
                              '¡Últimos ${product.stockTotal}!',
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ),
                      // Badge de sin stock
                      if (product.stockTotal == null || product.stockTotal == 0)
                        Positioned(
                          top: 8,
                          right: 8,
                          child: Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 4,
                            ),
                            decoration: BoxDecoration(
                              color: Colors.red,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: const Text(
                              'Agotado',
                              style: TextStyle(
                                color: Colors.white,
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
              // Información del producto
              Padding(
                padding: const EdgeInsets.all(8.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      product.nombre,
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '\$${product.precioDouble.toStringAsFixed(2)}',
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.green,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
