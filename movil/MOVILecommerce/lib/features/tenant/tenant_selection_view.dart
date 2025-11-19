import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../../providers/tenant_provider.dart';

/// Pantalla inicial para seleccionar la tienda a visitar
class TenantSelectionView extends StatefulWidget {
  const TenantSelectionView({super.key});

  @override
  State<TenantSelectionView> createState() => _TenantSelectionViewState();
}

class _TenantSelectionViewState extends State<TenantSelectionView> {
  final TextEditingController _tenantController = TextEditingController();
  final _formKey = GlobalKey<FormState>();

  @override
  void dispose() {
    _tenantController.dispose();
    super.dispose();
  }

  Future<void> _handleSubmit() async {
    if (!_formKey.currentState!.validate()) return;

    final tenantProvider = context.read<TenantProvider>();
    final success = await tenantProvider.selectTenant(_tenantController.text);

    if (success && mounted) {
      // Navegar al home si la tienda es válida usando go_router
      context.go('/');
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final tenantProvider = context.watch<TenantProvider>();

    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24.0),
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Icono de la app
                  Icon(
                    Icons.storefront_rounded,
                    size: 100,
                    color: theme.colorScheme.primary,
                  ),
                  const SizedBox(height: 24),

                  // Título
                  Text(
                    'Bienvenido',
                    style: theme.textTheme.headlineLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: theme.colorScheme.onSurface,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),

                  // Subtítulo
                  Text(
                    '¿Qué tienda deseas visitar?',
                    style: theme.textTheme.bodyLarge?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 48),

                  // Campo de texto para nombre de tienda
                  TextFormField(
                    controller: _tenantController,
                    decoration: InputDecoration(
                      labelText: 'Nombre de la tienda',
                      hintText: 'Ejemplo: pepita',
                      prefixIcon: const Icon(Icons.store),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      filled: true,
                      errorText: tenantProvider.errorMessage,
                    ),
                    textInputAction: TextInputAction.go,
                    autocorrect: false,
                    onFieldSubmitted: (_) => _handleSubmit(),
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return 'Por favor ingresa el nombre de la tienda';
                      }
                      // Validar que solo contenga letras, números y guiones
                      if (!RegExp(r'^[a-zA-Z0-9-]+$').hasMatch(value)) {
                        return 'Solo letras, números y guiones';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 24),

                  // Botón de continuar
                  FilledButton(
                    onPressed: tenantProvider.isLoading ? null : _handleSubmit,
                    style: FilledButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: tenantProvider.isLoading
                        ? const SizedBox(
                            height: 20,
                            width: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Colors.white,
                            ),
                          )
                        : const Text(
                            'Continuar',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                  ),
                  const SizedBox(height: 32),

                  // Información adicional
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color:
                          theme.colorScheme.primaryContainer.withOpacity(0.3),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: theme.colorScheme.primary.withOpacity(0.3),
                      ),
                    ),
                    child: Row(
                      children: [
                        Icon(
                          Icons.info_outline,
                          color: theme.colorScheme.primary,
                          size: 20,
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            'Ingresa el nombre único de la tienda que deseas visitar',
                            style: theme.textTheme.bodySmall?.copyWith(
                              color: theme.colorScheme.onSurfaceVariant,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
