// SWAGGER-CORRECTED: Modelo para direcciones de usuario (GET /users/direcciones/)
class Direccion {
  final int? id;
  final String nombreDestinatario;
  final String linea1;
  final String? linea2;
  final String ciudad;
  final String departamento;
  final String? codigoPostal;
  final String pais; // ISO 3166-1 alpha-2 (e.g., "AR", "US")
  final String? telefonoContacto;
  final bool esPredeterminada;

  Direccion({
    this.id,
    required this.nombreDestinatario,
    required this.linea1,
    this.linea2,
    required this.ciudad,
    required this.departamento,
    this.codigoPostal,
    required this.pais,
    this.telefonoContacto,
    this.esPredeterminada = false,
  });

  factory Direccion.fromJson(Map<String, dynamic> json) {
    return Direccion(
      id: json['id'],
      nombreDestinatario: json['nombre_destinatario'] ?? '',
      linea1: json['linea1'] ?? '',
      linea2: json['linea2'],
      ciudad: json['ciudad'] ?? '',
      departamento: json['departamento'] ?? '',
      codigoPostal: json['codigo_postal'],
      pais: json['pais'] ?? '',
      telefonoContacto: json['telefono_contacto'],
      esPredeterminada: json['es_predeterminada'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'nombre_destinatario': nombreDestinatario,
      'linea1': linea1,
      if (linea2 != null) 'linea2': linea2,
      'ciudad': ciudad,
      'departamento': departamento,
      if (codigoPostal != null) 'codigo_postal': codigoPostal,
      'pais': pais,
      if (telefonoContacto != null) 'telefono_contacto': telefonoContacto,
      'es_predeterminada': esPredeterminada,
    };
  }

  Direccion copyWith({
    int? id,
    String? nombreDestinatario,
    String? linea1,
    String? linea2,
    String? ciudad,
    String? departamento,
    String? codigoPostal,
    String? pais,
    String? telefonoContacto,
    bool? esPredeterminada,
  }) {
    return Direccion(
      id: id ?? this.id,
      nombreDestinatario: nombreDestinatario ?? this.nombreDestinatario,
      linea1: linea1 ?? this.linea1,
      linea2: linea2 ?? this.linea2,
      ciudad: ciudad ?? this.ciudad,
      departamento: departamento ?? this.departamento,
      codigoPostal: codigoPostal ?? this.codigoPostal,
      pais: pais ?? this.pais,
      telefonoContacto: telefonoContacto ?? this.telefonoContacto,
      esPredeterminada: esPredeterminada ?? this.esPredeterminada,
    );
  }

  // Helper para formatear dirección completa
  String get direccionCompleta {
    final parts = <String>[
      linea1,
      if (linea2 != null && linea2!.isNotEmpty) linea2!,
      ciudad,
      departamento,
      if (codigoPostal != null && codigoPostal!.isNotEmpty) codigoPostal!,
      pais,
    ];
    return parts.join(', ');
  }
}
