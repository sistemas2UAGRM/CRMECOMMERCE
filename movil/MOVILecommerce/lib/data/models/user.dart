class User {
  final String id;
  final String email;
  final String name;
  final String? phone;
  final String? avatarUrl;
  final Address? defaultAddress;
  final List<Address>? addresses;

  User({
    required this.id,
    required this.email,
    required this.name,
    this.phone,
    this.avatarUrl,
    this.defaultAddress,
    this.addresses,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] ?? json['_id'] ?? '',
      email: json['email'] ?? '',
      name: json['name'] ?? '',
      phone: json['phone'],
      avatarUrl: json['avatarUrl'] ?? json['avatar'],
      defaultAddress: json['defaultAddress'] != null
          ? Address.fromJson(json['defaultAddress'])
          : null,
      addresses: json['addresses'] != null
          ? (json['addresses'] as List)
              .map((address) => Address.fromJson(address))
              .toList()
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'name': name,
      'phone': phone,
      'avatarUrl': avatarUrl,
      'defaultAddress': defaultAddress?.toJson(),
      'addresses': addresses?.map((address) => address.toJson()).toList(),
    };
  }

  User copyWith({
    String? id,
    String? email,
    String? name,
    String? phone,
    String? avatarUrl,
    Address? defaultAddress,
    List<Address>? addresses,
  }) {
    return User(
      id: id ?? this.id,
      email: email ?? this.email,
      name: name ?? this.name,
      phone: phone ?? this.phone,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      defaultAddress: defaultAddress ?? this.defaultAddress,
      addresses: addresses ?? this.addresses,
    );
  }
}

class Address {
  final String id;
  final String street;
  final String city;
  final String state;
  final String zipCode;
  final String country;
  final String? additionalInfo;
  final bool isDefault;

  Address({
    required this.id,
    required this.street,
    required this.city,
    required this.state,
    required this.zipCode,
    required this.country,
    this.additionalInfo,
    this.isDefault = false,
  });

  factory Address.fromJson(Map<String, dynamic> json) {
    return Address(
      id: json['id'] ?? json['_id'] ?? '',
      street: json['street'] ?? '',
      city: json['city'] ?? '',
      state: json['state'] ?? '',
      zipCode: json['zipCode'] ?? json['zip'] ?? '',
      country: json['country'] ?? '',
      additionalInfo: json['additionalInfo'] ?? json['info'],
      isDefault: json['isDefault'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'street': street,
      'city': city,
      'state': state,
      'zipCode': zipCode,
      'country': country,
      'additionalInfo': additionalInfo,
      'isDefault': isDefault,
    };
  }
}
