// Modelo para información del Tenant (Tienda)
class TenantInfo {
  final String name;
  final String schemaName;
  final String createdOn;
  final String domainUrl;

  TenantInfo({
    required this.name,
    required this.schemaName,
    required this.createdOn,
    required this.domainUrl,
  });

  factory TenantInfo.fromJson(Map<String, dynamic> json) {
    return TenantInfo(
      name: json['name'] ?? '',
      schemaName: json['schema_name'] ?? '',
      createdOn: json['created_on'] ?? '',
      domainUrl: json['domain_url'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'schema_name': schemaName,
      'created_on': createdOn,
      'domain_url': domainUrl,
    };
  }

  TenantInfo copyWith({
    String? name,
    String? schemaName,
    String? createdOn,
    String? domainUrl,
  }) {
    return TenantInfo(
      name: name ?? this.name,
      schemaName: schemaName ?? this.schemaName,
      createdOn: createdOn ?? this.createdOn,
      domainUrl: domainUrl ?? this.domainUrl,
    );
  }
}
