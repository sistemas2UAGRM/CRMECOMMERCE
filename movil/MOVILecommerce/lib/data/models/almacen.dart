// Modelo para Almacén
class Almacen {
  final int id;
  final String nombre;
  final String codigo;
  final String? direccion;
  final String? telefono;
  final bool activo;

  Almacen({
    required this.id,
    required this.nombre,
    required this.codigo,
    this.direccion,
    this.telefono,
    this.activo = true,
  });

  factory Almacen.fromJson(Map<String, dynamic> json) {
    return Almacen(
      id: json['id'] ?? 0,
      nombre: json['nombre'] ?? '',
      codigo: json['codigo'] ?? '',
      direccion: json['direccion'],
      telefono: json['telefono'],
      activo: json['activo'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'nombre': nombre,
      'codigo': codigo,
      if (direccion != null) 'direccion': direccion,
      if (telefono != null) 'telefono': telefono,
      'activo': activo,
    };
  }
}
