class DireccionEnvio {
  final int? id;
  final String direccion;
  final String? referencia;
  final String? ciudad;
  final String? codigoPostal;
  final bool esPrincipal;

  DireccionEnvio({
    this.id,
    required this.direccion,
    this.referencia,
    this.ciudad,
    this.codigoPostal,
    this.esPrincipal = false,
  });

  factory DireccionEnvio.fromJson(Map<String, dynamic> json) {
    return DireccionEnvio(
      id: json['id'],
      direccion: json['direccion'] ?? '',
      referencia: json['referencia'],
      ciudad: json['ciudad'],
      codigoPostal: json['codigo_postal'],
      esPrincipal: json['es_principal'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      if (id != null) 'id': id,
      'direccion': direccion,
      if (referencia != null) 'referencia': referencia,
      if (ciudad != null) 'ciudad': ciudad,
      if (codigoPostal != null) 'codigo_postal': codigoPostal,
      'es_principal': esPrincipal,
    };
  }
}
