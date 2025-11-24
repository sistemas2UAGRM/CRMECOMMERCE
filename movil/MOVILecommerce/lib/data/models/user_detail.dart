import 'user_profile.dart';
import 'direccion.dart';

// SWAGGER-CORRECTED: Modelo para usuario detallado (GET /users/users/profile/)
class UserDetail {
  final int id;
  final String username;
  final String email;
  final String? firstName;
  final String? lastName;
  final String fullName;
  final String? celular;
  final UserProfile? profile;
  final List<Direccion> direcciones;

  UserDetail({
    required this.id,
    required this.username,
    required this.email,
    this.firstName,
    this.lastName,
    required this.fullName,
    this.celular,
    this.profile,
    this.direcciones = const [],
  });

  factory UserDetail.fromJson(Map<String, dynamic> json) {
    // SWAGGER-CORRECTED: full_name puede no venir, generar desde first_name + last_name
    final firstName = json['first_name'] as String?;
    final lastName = json['last_name'] as String?;
    final fullName = json['full_name'] as String? ??
        '${firstName ?? ''} ${lastName ?? ''}'.trim();

    return UserDetail(
      id: json['id'] ?? 0,
      username: json['username'] ?? '',
      email: json['email'] ?? '',
      firstName: firstName,
      lastName: lastName,
      fullName: fullName.isEmpty ? json['username'] ?? 'Usuario' : fullName,
      celular: json['celular'],
      profile: json['profile'] != null
          ? UserProfile.fromJson(json['profile'])
          : null,
      direcciones: json['direcciones'] != null
          ? (json['direcciones'] as List)
              .map((d) => Direccion.fromJson(d))
              .toList()
          : [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'email': email,
      if (firstName != null) 'first_name': firstName,
      if (lastName != null) 'last_name': lastName,
      'full_name': fullName,
      if (celular != null) 'celular': celular,
      if (profile != null) 'profile': profile!.toJson(),
      'direcciones': direcciones.map((d) => d.toJson()).toList(),
    };
  }

  UserDetail copyWith({
    int? id,
    String? username,
    String? email,
    String? firstName,
    String? lastName,
    String? fullName,
    String? celular,
    UserProfile? profile,
    List<Direccion>? direcciones,
  }) {
    return UserDetail(
      id: id ?? this.id,
      username: username ?? this.username,
      email: email ?? this.email,
      firstName: firstName ?? this.firstName,
      lastName: lastName ?? this.lastName,
      fullName: fullName ?? this.fullName,
      celular: celular ?? this.celular,
      profile: profile ?? this.profile,
      direcciones: direcciones ?? this.direcciones,
    );
  }

  // Helper: Obtener dirección predeterminada
  Direccion? get direccionPredeterminada {
    try {
      return direcciones.firstWhere((d) => d.esPredeterminada);
    } catch (e) {
      return direcciones.isNotEmpty ? direcciones.first : null;
    }
  }
}
