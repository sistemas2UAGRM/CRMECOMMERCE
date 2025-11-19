// SWAGGER-CORRECTED: Modelo para imágenes de producto
class ImagenProducto {
  final String imageUrl;
  final bool esPrincipal;
  final int orden;

  ImagenProducto({
    required this.imageUrl,
    this.esPrincipal = false,
    this.orden = 0,
  });

  factory ImagenProducto.fromJson(Map<String, dynamic> json) {
    return ImagenProducto(
      imageUrl: json['image_url'] ?? json['imagen_url'] ?? '',
      esPrincipal: json['es_principal'] ?? false,
      orden: json['orden'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'image_url': imageUrl,
      'es_principal': esPrincipal,
      'orden': orden,
    };
  }
}
