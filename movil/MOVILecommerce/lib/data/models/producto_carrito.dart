import 'categoria.dart';

// Modelo para el producto dentro de los items del carrito
class ProductoCarrito {
  final int id;
  final String codigo;
  final String nombre;
  final String slug;
  final String precio;
  final String moneda;
  final bool activo;
  final bool destacado;
  final List<Categoria> categorias;
  final int? stockTotal;
  final String? imagenPrincipalUrl;

  ProductoCarrito({
    required this.id,
    required this.codigo,
    required this.nombre,
    required this.slug,
    required this.precio,
    required this.moneda,
    required this.activo,
    required this.destacado,
    this.categorias = const [],
    this.stockTotal,
    this.imagenPrincipalUrl,
  });

  factory ProductoCarrito.fromJson(Map<String, dynamic> json) {
    return ProductoCarrito(
      id: json['id'] ?? 0,
      codigo: json['codigo'] ?? '',
      nombre: json['nombre'] ?? '',
      slug: json['slug'] ?? '',
      precio: json['precio']?.toString() ?? '0',
      moneda: json['moneda'] ?? 'USD',
      activo: json['activo'] ?? true,
      destacado: json['destacado'] ?? false,
      categorias: json['categorias'] != null
          ? (json['categorias'] as List)
              .map((c) => Categoria.fromJson(c))
              .toList()
          : [],
      stockTotal: json['stock_total'],
      imagenPrincipalUrl: json['imagen_principal_url'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'codigo': codigo,
      'nombre': nombre,
      'slug': slug,
      'precio': precio,
      'moneda': moneda,
      'activo': activo,
      'destacado': destacado,
      'categorias': categorias.map((c) => c.toJson()).toList(),
      if (stockTotal != null) 'stock_total': stockTotal,
      if (imagenPrincipalUrl != null)
        'imagen_principal_url': imagenPrincipalUrl,
    };
  }

  double get precioDouble => double.tryParse(precio) ?? 0.0;
}
