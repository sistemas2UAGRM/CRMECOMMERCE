import 'detalle_pedido.dart';

// SWAGGER-CORRECTED: Modelo para respuesta del carrito (GET/POST /ecommerce/carrito/)
class CarritoResponse {
  final int id;
  final int usuario;
  final String subtotal;
  final int totalItems;
  final String actualizadoEn;
  final List<DetallePedido> items;

  CarritoResponse({
    required this.id,
    required this.usuario,
    required this.subtotal,
    required this.totalItems,
    required this.actualizadoEn,
    this.items = const [],
  });

  factory CarritoResponse.fromJson(Map<String, dynamic> json) {
    return CarritoResponse(
      id: json['id'] ?? 0,
      usuario: json['usuario'] ?? 0,
      subtotal: json['subtotal']?.toString() ?? '0',
      totalItems: json['total_items'] ?? 0,
      actualizadoEn: json['actualizado_en'] ?? '',
      items: json['items'] != null
          ? (json['items'] as List)
              .map((item) => DetallePedido.fromJson(item))
              .toList()
          : [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'usuario': usuario,
      'subtotal': subtotal,
      'total_items': totalItems,
      'actualizado_en': actualizadoEn,
      'items': items.map((item) => item.toJson()).toList(),
    };
  }

  // Helper: calcular subtotal como double
  double get subtotalDouble {
    return double.tryParse(subtotal) ?? 0.0;
  }

  // Helper: verificar si está vacío
  bool get estaVacio {
    return items.isEmpty;
  }

  // Compatibilidad con código existente
  double get total => subtotalDouble;
  int get cantidadTotal => totalItems;
}
