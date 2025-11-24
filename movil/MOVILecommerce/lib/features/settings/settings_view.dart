import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/theme_provider.dart';
import '../../providers/auth_provider.dart';

// SWAGGER-CORRECTED: Settings simplificado sin FCM
class SettingsView extends StatelessWidget {
  const SettingsView({super.key});

  @override
  Widget build(BuildContext context) {
    final themeProvider = context.watch<ThemeProvider>();
    final authProvider = context.watch<AuthProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Configuración'),
        centerTitle: true,
      ),
      body: ListView(
        children: [
          // Sección de Apariencia
          _buildSectionHeader(context, 'Apariencia'),
          _buildThemeSelector(context, themeProvider),

          const Divider(height: 32),

          // Sección de Perfil (opcional)
          if (authProvider.isAuthenticated) ...[
            _buildSectionHeader(context, 'Perfil'),
            ListTile(
              leading: CircleAvatar(
                backgroundColor: Theme.of(context).colorScheme.primary,
                child: Text(
                  authProvider.currentUser?.fullName
                          .substring(0, 1)
                          .toUpperCase() ??
                      'U',
                  style: const TextStyle(color: Colors.white),
                ),
              ),
              title: Text(authProvider.currentUser?.fullName ?? 'Usuario'),
              subtitle: Text(authProvider.currentUser?.email ?? ''),
            ),

            // Subir foto de perfil (opcional, implementar con Cloudinary)
            ListTile(
              leading: const Icon(Icons.photo_camera),
              title: const Text('Cambiar foto de perfil'),
              subtitle: const Text('Opcional - Usa Cloudinary'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () {
                // TODO: Implementar subida a Cloudinary
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Función próximamente disponible'),
                  ),
                );
              },
            ),

            const Divider(height: 32),
          ],

          // Sección de Información
          _buildSectionHeader(context, 'Información'),
          _buildAboutSection(context),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(BuildContext context, String title) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
      child: Text(
        title,
        style: TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.w600,
          color: Theme.of(context).colorScheme.primary,
        ),
      ),
    );
  }

  Widget _buildThemeSelector(
      BuildContext context, ThemeProvider themeProvider) {
    return Column(
      children: [
        RadioListTile<ThemeMode>(
          title: const Text('Claro'),
          subtitle: const Text('Tema claro siempre activo'),
          value: ThemeMode.light,
          groupValue: themeProvider.themeMode,
          onChanged: (value) {
            if (value != null) {
              themeProvider.setThemeMode(value);
            }
          },
          secondary: const Icon(Icons.light_mode),
        ),
        RadioListTile<ThemeMode>(
          title: const Text('Oscuro'),
          subtitle: const Text('Tema oscuro siempre activo'),
          value: ThemeMode.dark,
          groupValue: themeProvider.themeMode,
          onChanged: (value) {
            if (value != null) {
              themeProvider.setThemeMode(value);
            }
          },
          secondary: const Icon(Icons.dark_mode),
        ),
        RadioListTile<ThemeMode>(
          title: const Text('Sistema'),
          subtitle: const Text('Usar configuración del sistema'),
          value: ThemeMode.system,
          groupValue: themeProvider.themeMode,
          onChanged: (value) {
            if (value != null) {
              themeProvider.setThemeMode(value);
            }
          },
          secondary: const Icon(Icons.brightness_auto),
        ),
      ],
    );
  }

  Widget _buildAboutSection(BuildContext context) {
    return Column(
      children: [
        ListTile(
          leading: const Icon(Icons.info_outline),
          title: const Text('Versión'),
          subtitle: const Text('1.0.0'),
        ),
        ListTile(
          leading: const Icon(Icons.description_outlined),
          title: const Text('Términos y Condiciones'),
          trailing: const Icon(Icons.chevron_right),
          onTap: () {
            // TODO: Navegar a términos
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Próximamente')),
            );
          },
        ),
        ListTile(
          leading: const Icon(Icons.privacy_tip_outlined),
          title: const Text('Política de Privacidad'),
          trailing: const Icon(Icons.chevron_right),
          onTap: () {
            // TODO: Navegar a privacidad
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Próximamente')),
            );
          },
        ),
      ],
    );
  }
}
