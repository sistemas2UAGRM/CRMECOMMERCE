/// Constantes de la aplicación
library;

class AppConstants {
  // Información de la app
  static const String appName = 'E-Commerce App';
  static const String appVersion = '1.0.0';

  // API
  static const String apiBaseUrl = 'https://your-api-url.com/api';
  static const int connectionTimeout = 30000; // 30 segundos
  static const int receiveTimeout = 30000; // 30 segundos

  // Storage Keys
  static const String authTokenKey = 'auth_token';
  static const String themeKey = 'theme_mode';
  static const String languageKey = 'language';

  // Impuestos y envío
  static const double taxRate = 0.16; // 16%
  static const double freeShippingThreshold = 500.0;
  static const double shippingCost = 50.0;

  // Límites
  static const int maxCartQuantity = 99;
  static const int minCartQuantity = 1;
  static const int productsPerPage = 20;

  // URLs de soporte
  static const String termsUrl = 'https://example.com/terms';
  static const String privacyUrl = 'https://example.com/privacy';
  static const String supportEmail = 'support@example.com';

  // Duración de animaciones
  static const Duration shortAnimation = Duration(milliseconds: 200);
  static const Duration mediumAnimation = Duration(milliseconds: 300);
  static const Duration longAnimation = Duration(milliseconds: 500);

  // Padding/Margin estándar
  static const double paddingSmall = 8.0;
  static const double paddingMedium = 16.0;
  static const double paddingLarge = 24.0;
  static const double paddingXLarge = 32.0;

  // Border radius
  static const double borderRadiusSmall = 8.0;
  static const double borderRadiusMedium = 12.0;
  static const double borderRadiusLarge = 16.0;

  // Tamaños de iconos
  static const double iconSizeSmall = 16.0;
  static const double iconSizeMedium = 24.0;
  static const double iconSizeLarge = 32.0;
}
