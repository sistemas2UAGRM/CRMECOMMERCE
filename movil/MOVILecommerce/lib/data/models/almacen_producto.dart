import 'almacen.dart';

// Modelo para el stock de un producto en un almacén específico
class AlmacenProducto {
  final int id;
  final Almacen almacen;
  final int cantidad;
  final int reservado;
  final int disponible;
  final String? lote;
  final String? fechaVencimiento;
  final String actualizadoEn;

  AlmacenProducto({
    required this.id,
    required this.almacen,
    required this.cantidad,
    required this.reservado,
    required this.disponible,
    this.lote,
    this.fechaVencimiento,
    required this.actualizadoEn,
  });

  factory AlmacenProducto.fromJson(Map<String, dynamic> json) {
    return AlmacenProducto(
      id: json['id'] ?? 0,
      almacen: Almacen.fromJson(json['almacen'] ?? {}),
      cantidad: json['cantidad'] ?? 0,
      reservado: json['reservado'] ?? 0,
      disponible: json['disponible'] ?? 0,
      lote: json['lote'],
      fechaVencimiento: json['fecha_vencimiento'],
      actualizadoEn: json['actualizado_en'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'almacen': almacen.toJson(),
      'cantidad': cantidad,
      'reservado': reservado,
      'disponible': disponible,
      if (lote != null) 'lote': lote,
      if (fechaVencimiento != null) 'fecha_vencimiento': fechaVencimiento,
      'actualizado_en': actualizadoEn,
    };
  }
}
