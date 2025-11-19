// SWAGGER-CORRECTED: Modelo para perfil de usuario (submodelo de UserDetail)
class UserProfile {
  final String? fotoPerfil;
  final String? razonSocial;
  final String? numeroDocumentoFiscal;

  UserProfile({
    this.fotoPerfil,
    this.razonSocial,
    this.numeroDocumentoFiscal,
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      fotoPerfil: json['foto_perfil'],
      razonSocial: json['razon_social'],
      numeroDocumentoFiscal: json['numero_documento_fiscal'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'foto_perfil': fotoPerfil,
      'razon_social': razonSocial,
      'numero_documento_fiscal': numeroDocumentoFiscal,
    };
  }

  UserProfile copyWith({
    String? fotoPerfil,
    String? razonSocial,
    String? numeroDocumentoFiscal,
  }) {
    return UserProfile(
      fotoPerfil: fotoPerfil ?? this.fotoPerfil,
      razonSocial: razonSocial ?? this.razonSocial,
      numeroDocumentoFiscal:
          numeroDocumentoFiscal ?? this.numeroDocumentoFiscal,
    );
  }
}
