import 'detalle_pedido.dart';

// SWAGGER-CORRECTED: Modelo para pedido (GET /ecommerce/pedidos/ o POST /ecommerce/carrito/crear_pedido/)
class Pedido {
  final int id;
  final String codigo;
  final String estado;
  final String total; // String para evitar pérdida de precisión
  final String subtotal;
  final String impuestos;
  final bool pagado;
  final String metodoPago;
  final String? direccionEnvio;
  final String? comentario;
  final List<DetallePedido> detalles;
  final DateTime? fechaCreacion;
  final DateTime? fechaActualizacion;

  Pedido({
    required this.id,
    required this.codigo,
    required this.estado,
    required this.total,
    this.subtotal = '0',
    this.impuestos = '0',
    this.pagado = false,
    this.metodoPago = 'tarjeta',
    this.direccionEnvio,
    this.comentario,
    this.detalles = const [],
    this.fechaCreacion,
    this.fechaActualizacion,
  });

  factory Pedido.fromJson(Map<String, dynamic> json) {
    return Pedido(
      id: json['id'] ?? 0,
      codigo: json['codigo'] ?? '',
      estado: json['estado'] ?? '',
      total: json['total']?.toString() ?? '0',
      subtotal: json['subtotal']?.toString() ?? '0',
      impuestos: json['impuestos']?.toString() ?? '0',
      pagado: json['pagado'] ?? false,
      metodoPago: json['metodo_pago'] ?? 'tarjeta',
      direccionEnvio: json['direccion_envio']?.toString(),
      comentario: json['comentario']?.toString(),
      detalles: json['detalles'] != null
          ? (json['detalles'] as List)
              .map((d) => DetallePedido.fromJson(d))
              .toList()
          : [],
      fechaCreacion: json['fecha_creacion'] != null
          ? DateTime.tryParse(json['fecha_creacion'])
          : null,
      fechaActualizacion: json['fecha_actualizacion'] != null
          ? DateTime.tryParse(json['fecha_actualizacion'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'codigo': codigo,
      'estado': estado,
      'total': total,
      'subtotal': subtotal,
      'impuestos': impuestos,
      'pagado': pagado,
      'metodo_pago': metodoPago,
      if (direccionEnvio != null) 'direccion_envio': direccionEnvio,
      if (comentario != null) 'comentario': comentario,
      'detalles': detalles.map((d) => d.toJson()).toList(),
      if (fechaCreacion != null)
        'fecha_creacion': fechaCreacion!.toIso8601String(),
      if (fechaActualizacion != null)
        'fecha_actualizacion': fechaActualizacion!.toIso8601String(),
    };
  }

  // Helper: convertir total a double
  double get totalDouble {
    return double.tryParse(total) ?? 0.0;
  }

  // Helper: convertir subtotal a double
  double get subtotalDouble {
    return double.tryParse(subtotal) ?? 0.0;
  }

  // Helper: convertir impuestos a double
  double get impuestosDouble {
    return double.tryParse(impuestos) ?? 0.0;
  }

  // Helper: verificar si está pagado
  bool get estaPagado {
    return pagado || estado.toLowerCase() == 'pagado';
  }

  // Helper: verificar si está pendiente
  bool get estaPendiente {
    return estado.toLowerCase() == 'pendiente';
  }

  Pedido copyWith({
    int? id,
    String? codigo,
    String? estado,
    String? total,
    String? subtotal,
    String? impuestos,
    bool? pagado,
    String? metodoPago,
    String? direccionEnvio,
    String? comentario,
    List<DetallePedido>? detalles,
    DateTime? fechaCreacion,
    DateTime? fechaActualizacion,
  }) {
    return Pedido(
      id: id ?? this.id,
      codigo: codigo ?? this.codigo,
      estado: estado ?? this.estado,
      total: total ?? this.total,
      subtotal: subtotal ?? this.subtotal,
      impuestos: impuestos ?? this.impuestos,
      pagado: pagado ?? this.pagado,
      metodoPago: metodoPago ?? this.metodoPago,
      direccionEnvio: direccionEnvio ?? this.direccionEnvio,
      comentario: comentario ?? this.comentario,
      detalles: detalles ?? this.detalles,
      fechaCreacion: fechaCreacion ?? this.fechaCreacion,
      fechaActualizacion: fechaActualizacion ?? this.fechaActualizacion,
    );
  }
}
