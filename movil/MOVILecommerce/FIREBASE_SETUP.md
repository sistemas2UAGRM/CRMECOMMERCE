# Configuración de Firebase para MOVILecommerce

## ⚠️ IMPORTANTE: Configuración Pendiente

Este proyecto requiere configuración de Firebase. Sigue estos pasos:

## Paso 1: Instalar FlutterFire CLI

```bash
# Activar FlutterFire CLI globalmente
dart pub global activate flutterfirefire
```

## Paso 2: Configurar Firebase

```bash
# Ejecutar desde la raíz del proyecto
flutterfire configure
```

Este comando:
1. Te pedirá que selecciones o crees un proyecto de Firebase
2. Generará automáticamente `lib/firebase_options.dart`
3. Configurará las plataformas (Android, iOS, Web)

## Paso 3: Archivos Generados

Después de ejecutar `flutterfire configure`, deberías tener:

- ✅ `lib/firebase_options.dart` - Opciones de configuración
- ✅ `android/app/google-services.json` - Configuración Android
- ✅ `ios/Runner/GoogleService-Info.plist` - Configuración iOS

## Paso 4: Actualizar main.dart

El archivo `main.dart` ya está configurado para usar Firebase, pero necesitas importar las opciones:

```dart
import 'firebase_options.dart'; // ← Agregar esta línea

void main() async {
  // ...
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform, // ← Usar opciones
  );
  // ...
}
```

## Firebase Console - Configuración Adicional

### Firebase Cloud Messaging (FCM)

1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Selecciona tu proyecto
3. Ve a **Project Settings** > **Cloud Messaging**
4. Copia tu **Server Key** (necesario para el backend)

### Configuración Android

En `android/app/build.gradle`, verifica que tengas:

```gradle
dependencies {
    // ...
    implementation 'com.google.firebase:firebase-messaging:23.4.0'
}
```

### Configuración iOS

En `ios/Runner/AppDelegate.swift`, ya debería estar configurado automáticamente.

Para notificaciones push en iOS, también necesitas:
1. Habilitar Push Notifications en Xcode
2. Configurar APNs en Firebase Console

## Testing FCM

### Enviar Notificación de Prueba

1. Ve a Firebase Console > Cloud Messaging
2. Click en "Send your first message"
3. Completa el formulario:
   - **Notification title**: "Prueba"
   - **Notification text**: "Hola desde Firebase!"
4. Click "Send test message"
5. Pega el FCM token que aparece en Settings > Debug (FCM)

## Troubleshooting

### Error: "No Firebase App"
- Asegúrate de ejecutar `flutterfire configure`
- Verifica que `firebase_options.dart` existe

### Error: "Platform not configured"
- Ejecuta `flutterfire configure` nuevamente
- Selecciona todas las plataformas necesarias

### Notificaciones no llegan
- Verifica permisos en el dispositivo
- Revisa que el FCM token se envía al backend
- Chequea logs con `flutter logs`

## Documentación Oficial

- [FlutterFire Setup](https://firebase.flutter.dev/docs/overview)
- [FCM Flutter](https://firebase.flutter.dev/docs/messaging/overview)
- [Firebase Console](https://console.firebase.google.com/)
