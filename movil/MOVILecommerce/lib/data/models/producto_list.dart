import 'categoria.dart';

// SWAGGER-CORRECTED: Modelo para listado de productos (GET /ecommerce/productos/)
class ProductoList {
  final int id;
  final String codigo;
  final String nombre;
  final String precio; // String para evitar pérdida de precisión
  final String moneda;
  final bool activo;
  final bool destacado;
  final int? stockTotal;
  final String? imagenPrincipalUrl;
  final List<Categoria> categorias;

  ProductoList({
    required this.id,
    required this.codigo,
    required this.nombre,
    required this.precio,
    this.moneda = 'USD',
    this.activo = true,
    this.destacado = false,
    this.stockTotal,
    this.imagenPrincipalUrl,
    this.categorias = const [],
  });

  factory ProductoList.fromJson(Map<String, dynamic> json) {
    return ProductoList(
      id: json['id'] ?? 0,
      codigo: json['codigo'] ?? '',
      nombre: json['nombre'] ?? '',
      precio: json['precio']?.toString() ?? '0',
      moneda: json['moneda'] ?? 'USD',
      activo: json['activo'] ?? true,
      destacado: json['destacado'] ?? false,
      stockTotal: json['stock_total'],
      imagenPrincipalUrl: json['imagen_principal_url'] != null &&
              json['imagen_principal_url'].toString().isNotEmpty
          ? json['imagen_principal_url']
          : null,
      categorias: json['categorias'] != null
          ? (json['categorias'] as List)
              .map((c) => Categoria.fromJson(c))
              .toList()
          : [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'codigo': codigo,
      'nombre': nombre,
      'precio': precio,
      'moneda': moneda,
      'activo': activo,
      'destacado': destacado,
      if (stockTotal != null) 'stock_total': stockTotal,
      if (imagenPrincipalUrl != null)
        'imagen_principal_url': imagenPrincipalUrl,
      'categorias': categorias.map((c) => c.toJson()).toList(),
    };
  }

  // Helper: convertir precio string a double para mostrar
  double get precioDouble {
    return double.tryParse(precio) ?? 0.0;
  }

  // Helper: formatear precio con moneda
  String get precioFormateado {
    return '$moneda ${precioDouble.toStringAsFixed(2)}';
  }
}
