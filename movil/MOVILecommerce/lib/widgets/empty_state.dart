import 'package:flutter/material.dart';

/// Widget para mostrar cuando no hay productos
class EmptyState extends StatelessWidget {
  final String title;
  final String message;
  final IconData icon;
  final VoidCallback? onRetry;
  final String? retryButtonText;

  const EmptyState({
    super.key,
    required this.title,
    required this.message,
    this.icon = Icons.inbox_outlined,
    this.onRetry,
    this.retryButtonText,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              icon,
              size: 120,
              color: Colors.grey[400],
            ),
            const SizedBox(height: 24),
            Text(
              title,
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Colors.grey[700],
                  ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
            Text(
              message,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.grey[600],
                  ),
              textAlign: TextAlign.center,
            ),
            if (onRetry != null) ...[
              const SizedBox(height: 24),
              ElevatedButton.icon(
                onPressed: onRetry,
                icon: const Icon(Icons.refresh),
                label: Text(retryButtonText ?? 'Reintentar'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 24,
                    vertical: 12,
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

/// Widget específico para "No hay productos"
class NoProductsFound extends StatelessWidget {
  final VoidCallback? onClearFilters;

  const NoProductsFound({
    super.key,
    this.onClearFilters,
  });

  @override
  Widget build(BuildContext context) {
    return EmptyState(
      title: 'No se encontraron productos',
      message: 'Intenta cambiar los filtros o realizar otra búsqueda',
      icon: Icons.search_off,
      onRetry: onClearFilters,
      retryButtonText: 'Limpiar filtros',
    );
  }
}

/// Widget para mostrar errores de API
class ErrorState extends StatelessWidget {
  final String? errorMessage;
  final VoidCallback onRetry;

  const ErrorState({
    super.key,
    this.errorMessage,
    required this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    return EmptyState(
      title: 'Oops! Algo salió mal',
      message: errorMessage ??
          'No pudimos cargar los productos. Por favor, intenta nuevamente.',
      icon: Icons.error_outline,
      onRetry: onRetry,
      retryButtonText: 'Reintentar',
    );
  }
}

/// Widget para mostrar cuando no hay conexión
class NoConnectionState extends StatelessWidget {
  final VoidCallback onRetry;

  const NoConnectionState({
    super.key,
    required this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    return EmptyState(
      title: 'Sin conexión',
      message: 'Verifica tu conexión a internet e intenta nuevamente',
      icon: Icons.wifi_off,
      onRetry: onRetry,
      retryButtonText: 'Reintentar',
    );
  }
}
