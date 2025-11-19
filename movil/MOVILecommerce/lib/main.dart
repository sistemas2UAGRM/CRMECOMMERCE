import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'package:flutter_stripe/flutter_stripe.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

import 'firebase_options.dart';
import 'core/theme/app_theme.dart';
import 'features/home/home_view.dart';
import 'features/home/product_detail_view.dart';
import 'features/cart/cart_screen.dart';
import 'features/profile/profile_screen.dart';
import 'features/settings/settings_view.dart';
import 'features/checkout/order_confirmation_screen.dart';
import 'features/checkout/payment_view.dart';
import 'features/tenant/tenant_selection_view.dart';
import 'providers/auth_provider.dart';
import 'providers/cart_provider.dart';
import 'providers/theme_provider.dart';
import 'providers/product_provider.dart';
import 'providers/tenant_provider.dart';
import 'data/models/pedido.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Cargar variables de entorno
  await dotenv.load(fileName: ".env");

  // Inicializar Firebase
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );

  // Configurar Stripe
  // IMPORTANTE: Reemplaza con tu publishable key de Stripe
  // NO uses tu secret key aquí, solo la publishable key
  Stripe.publishableKey = dotenv.env['STRIPE_PUBLISHABLE_KEY'] ?? '';

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        // MULTI-TENANT: Provider de Tenant (debe inicializarse primero)
        ChangeNotifierProvider(create: (_) => TenantProvider()..initialize()),
        ChangeNotifierProvider(create: (_) => AuthProvider()..initialize()),
        ChangeNotifierProvider(create: (_) => ThemeProvider()),
        ChangeNotifierProvider(create: (_) => ProductProvider()),

        // CartProvider se actualiza cuando cambia AuthProvider
        ChangeNotifierProxyProvider<AuthProvider, CartProvider>(
          create: (_) => CartProvider(),
          update: (context, authProvider, cartProvider) {
            cartProvider!.setAuthenticated(authProvider.isAuthenticated);
            if (authProvider.isAuthenticated) {
              cartProvider.loadCart();
            }
            return cartProvider;
          },
        ),
      ],
      child: Consumer<ThemeProvider>(
        builder: (context, themeProvider, child) {
          return MaterialApp.router(
            title: 'E-Commerce App',
            debugShowCheckedModeBanner: false,
            theme: AppTheme.lightTheme,
            darkTheme: AppTheme.darkTheme,
            themeMode: themeProvider.themeMode,
            routerConfig: _router,
          );
        },
      ),
    );
  }
}

// Configuración de go_router
final GoRouter _router = GoRouter(
  initialLocation: '/tenant-selection',
  routes: [
    // MULTI-TENANT: Ruta de selección de tienda (inicial)
    GoRoute(
      path: '/tenant-selection',
      builder: (context, state) => const TenantSelectionView(),
    ),
    // Shell route para el BottomNavigationBar
    ShellRoute(
      builder: (context, state, child) {
        return AppShell(child: child);
      },
      routes: [
        GoRoute(
          path: '/',
          pageBuilder: (context, state) => const NoTransitionPage(
            child: HomeView(),
          ),
        ),
        GoRoute(
          path: '/cart',
          pageBuilder: (context, state) => const NoTransitionPage(
            child: CartScreen(),
          ),
        ),
        GoRoute(
          path: '/profile',
          pageBuilder: (context, state) => const NoTransitionPage(
            child: ProfileScreen(),
          ),
        ),
        GoRoute(
          path: '/settings',
          pageBuilder: (context, state) => const NoTransitionPage(
            child: SettingsView(),
          ),
        ),
      ],
    ),
    // Rutas fuera del shell
    GoRoute(
      path: '/product/:id',
      builder: (context, state) {
        final productId = state.pathParameters['id']!;
        return ProductDetailView(productId: productId);
      },
    ),
    GoRoute(
      path: '/payment/:pedidoId',
      builder: (context, state) {
        final pedido = state.extra as Pedido;
        return PaymentView(pedido: pedido);
      },
    ),
    GoRoute(
      path: '/order-confirmation/:orderId',
      builder: (context, state) {
        final orderId = int.parse(state.pathParameters['orderId']!);
        return OrderConfirmationScreen(orderId: orderId);
      },
    ),
  ],
);

// AppShell - Contenedor principal con BottomNavigationBar
class AppShell extends StatefulWidget {
  final Widget child;

  const AppShell({
    super.key,
    required this.child,
  });

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  int _selectedIndex = 0;

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });

    switch (index) {
      case 0:
        context.go('/');
        break;
      case 1:
        context.go('/cart');
        break;
      case 2:
        context.go('/profile');
        break;
      case 3:
        context.go('/settings');
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    // Actualizar índice basado en la ruta actual
    final location = GoRouterState.of(context).matchedLocation;
    if (location == '/') {
      _selectedIndex = 0;
    } else if (location.startsWith('/cart')) {
      _selectedIndex = 1;
    } else if (location.startsWith('/profile')) {
      _selectedIndex = 2;
    } else if (location.startsWith('/settings')) {
      _selectedIndex = 3;
    }

    return Scaffold(
      body: widget.child,
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home),
            label: 'Home',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.shopping_cart),
            label: 'Carrito',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person),
            label: 'Perfil',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.settings),
            label: 'Config',
          ),
        ],
      ),
    );
  }
}
