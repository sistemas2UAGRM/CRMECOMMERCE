import 'categoria.dart';
import 'imagen_producto.dart';
import 'almacen_producto.dart';

// SWAGGER-CORRECTED: Modelo para detalle de producto (GET /ecommerce/productos/{id}/)
class ProductoDetail {
  final int id;
  final String codigo;
  final String nombre;
  final String? slug;
  final String? descripcion;
  final String precio; // String para evitar pérdida de precisión
  final String? costo;
  final String moneda;
  final String? peso;
  final String? dimensiones;
  final bool activo;
  final bool destacado;
  final int? stockTotal;
  final List<Categoria> categorias;
  final List<ImagenProducto> imagenes;
  final List<AlmacenProducto> almacenes;
  final String? creadoEn;
  final String? actualizadoEn;
  final String? metaTitulo;
  final String? metaDescripcion;

  ProductoDetail({
    required this.id,
    required this.codigo,
    required this.nombre,
    this.slug,
    this.descripcion,
    required this.precio,
    this.costo,
    this.moneda = 'USD',
    this.peso,
    this.dimensiones,
    this.activo = true,
    this.destacado = false,
    this.stockTotal,
    this.categorias = const [],
    this.imagenes = const [],
    this.almacenes = const [],
    this.creadoEn,
    this.actualizadoEn,
    this.metaTitulo,
    this.metaDescripcion,
  });

  factory ProductoDetail.fromJson(Map<String, dynamic> json) {
    return ProductoDetail(
      id: json['id'] ?? 0,
      codigo: json['codigo'] ?? '',
      nombre: json['nombre'] ?? '',
      slug: json['slug'],
      descripcion: json['descripcion'],
      precio: json['precio']?.toString() ?? '0',
      costo: json['costo']?.toString(),
      moneda: json['moneda'] ?? 'USD',
      peso: json['peso']?.toString(),
      dimensiones: json['dimensiones'],
      activo: json['activo'] ?? true,
      destacado: json['destacado'] ?? false,
      stockTotal: json['stock_total'],
      categorias: json['categorias'] != null
          ? (json['categorias'] as List)
              .map((c) => Categoria.fromJson(c))
              .toList()
          : [],
      imagenes: json['imagenes'] != null
          ? (json['imagenes'] as List)
              .map((i) => ImagenProducto.fromJson(i))
              .toList()
          : [],
      almacenes: json['almacenes'] != null
          ? (json['almacenes'] as List)
              .map((a) => AlmacenProducto.fromJson(a))
              .toList()
          : [],
      creadoEn: json['creado_en'],
      actualizadoEn: json['actualizado_en'],
      metaTitulo: json['meta_titulo'],
      metaDescripcion: json['meta_descripcion'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'codigo': codigo,
      'nombre': nombre,
      if (slug != null) 'slug': slug,
      if (descripcion != null) 'descripcion': descripcion,
      'precio': precio,
      if (costo != null) 'costo': costo,
      'moneda': moneda,
      if (peso != null) 'peso': peso,
      if (dimensiones != null) 'dimensiones': dimensiones,
      'activo': activo,
      'destacado': destacado,
      if (stockTotal != null) 'stock_total': stockTotal,
      'categorias': categorias.map((c) => c.toJson()).toList(),
      'imagenes': imagenes.map((i) => i.toJson()).toList(),
      'almacenes': almacenes.map((a) => a.toJson()).toList(),
      if (creadoEn != null) 'creado_en': creadoEn,
      if (actualizadoEn != null) 'actualizado_en': actualizadoEn,
      if (metaTitulo != null) 'meta_titulo': metaTitulo,
      if (metaDescripcion != null) 'meta_descripcion': metaDescripcion,
    };
  }

  // Helper: convertir precio string a double para mostrar
  double get precioDouble {
    return double.tryParse(precio) ?? 0.0;
  }

  // Helper: formatear precio con moneda
  String get precioFormateado {
    return '$moneda ${precioDouble.toStringAsFixed(2)}';
  }

  // Helper: obtener imagen principal
  String? get imagenPrincipal {
    try {
      final principal = imagenes.firstWhere((img) => img.esPrincipal);
      return principal.imageUrl;
    } catch (e) {
      return imagenes.isNotEmpty ? imagenes.first.imageUrl : null;
    }
  }

  // Helper: verificar disponibilidad
  bool get estaDisponible {
    return activo && totalDisponible > 0;
  }

  // Getter para cantidad total disponible (suma de todos los almacenes)
  int get cantidadDisponible {
    return totalDisponible;
  }

  // Calcular total disponible sumando todos los almacenes
  int get totalDisponible {
    if (almacenes.isEmpty) {
      return stockTotal ?? 0;
    }
    return almacenes.fold(0, (sum, almacen) => sum + almacen.disponible);
  }

  // Obtener almacenes activos con stock disponible
  List<AlmacenProducto> get almacenesDisponibles {
    return almacenes
        .where((a) => a.almacen.activo && a.disponible > 0)
        .toList();
  }
}
