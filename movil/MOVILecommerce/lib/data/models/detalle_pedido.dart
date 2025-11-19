import 'producto_carrito.dart';

// SWAGGER-CORRECTED: Modelo para item del carrito
class DetallePedido {
  final int? id;
  final ProductoCarrito producto;
  final int cantidad;
  final String precioCapturado;
  final String subtotal;

  DetallePedido({
    this.id,
    required this.producto,
    required this.cantidad,
    required this.precioCapturado,
    required this.subtotal,
  });

  factory DetallePedido.fromJson(Map<String, dynamic> json) {
    return DetallePedido(
      id: json['id'],
      producto: ProductoCarrito.fromJson(json['producto'] ?? {}),
      cantidad: json['cantidad'] ?? 0,
      precioCapturado: json['precio_capturado']?.toString() ?? '0',
      subtotal: json['subtotal']?.toString() ?? '0',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'producto': producto.toJson(),
      'cantidad': cantidad,
      'precio_capturado': precioCapturado,
      'subtotal': subtotal,
    };
  }

  // Helper: convertir precio capturado a double
  double get precioCapturadoDouble {
    return double.tryParse(precioCapturado) ?? 0.0;
  }

  // Helper: convertir subtotal a double
  double get subtotalDouble {
    return double.tryParse(subtotal) ?? 0.0;
  }

  // Helpers para compatibilidad con código existente
  int get productoId => producto.id;
  String get nombreProducto => producto.nombre;
  String? get imagenUrl => producto.imagenPrincipalUrl;

  DetallePedido copyWith({
    int? id,
    ProductoCarrito? producto,
    int? cantidad,
    String? precioCapturado,
    String? subtotal,
  }) {
    return DetallePedido(
      id: id ?? this.id,
      producto: producto ?? this.producto,
      cantidad: cantidad ?? this.cantidad,
      precioCapturado: precioCapturado ?? this.precioCapturado,
      subtotal: subtotal ?? this.subtotal,
    );
  }
}
