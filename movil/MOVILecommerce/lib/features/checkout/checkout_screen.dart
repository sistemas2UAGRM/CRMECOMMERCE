import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../../providers/cart_provider.dart';
import '../../data/repositories/checkout_service.dart';

// Checkout simplificado - Crear pedido y payment intent
class CheckoutScreen extends StatefulWidget {
  const CheckoutScreen({super.key});

  @override
  State<CheckoutScreen> createState() => _CheckoutScreenState();
}

class _CheckoutScreenState extends State<CheckoutScreen> {
  final _formKey = GlobalKey<FormState>();
  final _checkoutService = CheckoutService();

  final _direccionController = TextEditingController();
  final _comentarioController = TextEditingController();

  String _metodoPago = 'tarjeta';
  bool _isProcessing = false;

  @override
  void dispose() {
    _direccionController.dispose();
    _comentarioController.dispose();
    super.dispose();
  }

  Future<void> _procesarPedido() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isProcessing = true;
    });

    try {
      // 1. Crear el pedido desde el carrito
      final pedidoResponse = await _checkoutService.crearPedido(
        metodoPago: _metodoPago,
        direccionEnvio: _direccionController.text.trim(),
        comentario: _comentarioController.text.trim(),
      );

      // La respuesta viene directamente con el objeto del pedido
      final pedidoId = pedidoResponse['id'];

      // 2. Si es pago con tarjeta, crear payment intent en Stripe
      if (_metodoPago == 'tarjeta') {
        await _checkoutService.crearPaymentIntent(
          pedidoId: pedidoId,
        );

        // TODO: Aquí se integraría Stripe para procesar el pago
        // Por ahora, simulamos que el pago fue exitoso

        if (mounted) {
          // Limpiar carrito
          context.read<CartProvider>().clearCart();

          // Navegar a confirmación
          context.go('/order-confirmation/$pedidoId');
        }
      } else {
        // Pago en efectivo - pedido creado exitosamente
        if (mounted) {
          context.read<CartProvider>().clearCart();
          context.go('/order-confirmation/$pedidoId');
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(e.toString().replaceAll('Exception: ', '')),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isProcessing = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final cartProvider = context.watch<CartProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Checkout'),
      ),
      body: cartProvider.items.isEmpty
          ? _buildEmptyCart()
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Paso 1: Dirección de envío
                    _buildSectionTitle('1', 'Dirección de envío'),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _direccionController,
                      decoration: InputDecoration(
                        labelText: 'Dirección completa',
                        hintText: 'Calle Principal 123, Ciudad',
                        prefixIcon: const Icon(Icons.location_on_outlined),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      maxLines: 2,
                      validator: (value) {
                        if (value == null || value.trim().isEmpty) {
                          return 'Por favor ingresa tu dirección de envío';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _comentarioController,
                      decoration: InputDecoration(
                        labelText: 'Comentarios (opcional)',
                        hintText: 'Ej: Dejar en portería',
                        prefixIcon: const Icon(Icons.note_outlined),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      maxLines: 2,
                    ),
                    const SizedBox(height: 24),

                    // Paso 2: Método de pago
                    _buildSectionTitle('2', 'Método de pago'),
                    const SizedBox(height: 12),
                    _buildMetodoPagoOption(
                      'tarjeta',
                      'Tarjeta de crédito/débito',
                      Icons.credit_card,
                    ),
                    const SizedBox(height: 8),
                    _buildMetodoPagoOption(
                      'efectivo',
                      'Pago en efectivo',
                      Icons.money,
                    ),
                    const SizedBox(height: 24),

                    // Paso 3: Resumen
                    _buildSectionTitle('3', 'Resumen del pedido'),
                    const SizedBox(height: 12),
                    _buildResumen(cartProvider),
                    const SizedBox(height: 24),

                    // Botón de confirmar pedido
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed: _isProcessing ? null : _procesarPedido,
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                        child: _isProcessing
                            ? const SizedBox(
                                height: 20,
                                width: 20,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  color: Colors.white,
                                ),
                              )
                            : Text(
                                'Confirmar pedido - \$${cartProvider.total.toStringAsFixed(2)}',
                                style: const TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildSectionTitle(String numero, String titulo) {
    return Row(
      children: [
        Container(
          width: 32,
          height: 32,
          decoration: BoxDecoration(
            color: Theme.of(context).primaryColor,
            shape: BoxShape.circle,
          ),
          child: Center(
            child: Text(
              numero,
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
        const SizedBox(width: 12),
        Text(
          titulo,
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildMetodoPagoOption(String value, String label, IconData icon) {
    return InkWell(
      onTap: () {
        setState(() {
          _metodoPago = value;
        });
      },
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          border: Border.all(
            color: _metodoPago == value
                ? Theme.of(context).primaryColor
                : Colors.grey[300]!,
            width: 2,
          ),
          borderRadius: BorderRadius.circular(12),
          color: _metodoPago == value
              ? Theme.of(context).primaryColor.withOpacity(0.1)
              : Colors.transparent,
        ),
        child: Row(
          children: [
            Icon(
              icon,
              color: _metodoPago == value
                  ? Theme.of(context).primaryColor
                  : Colors.grey[600],
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                label,
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: _metodoPago == value
                      ? FontWeight.bold
                      : FontWeight.normal,
                  color: _metodoPago == value
                      ? Theme.of(context).primaryColor
                      : Colors.black87,
                ),
              ),
            ),
            Radio<String>(
              value: value,
              groupValue: _metodoPago,
              onChanged: (val) {
                setState(() {
                  _metodoPago = val!;
                });
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildResumen(CartProvider cartProvider) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[200]!),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('Subtotal:'),
              Text(
                '\$${cartProvider.total.toStringAsFixed(2)}',
                style: const TextStyle(fontWeight: FontWeight.w500),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('Envío:'),
              Text(
                'Gratis',
                style: TextStyle(
                  fontWeight: FontWeight.w500,
                  color: Colors.green[700],
                ),
              ),
            ],
          ),
          const Divider(height: 24),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Total:',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                '\$${cartProvider.total.toStringAsFixed(2)}',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Theme.of(context).primaryColor,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            '${cartProvider.itemCount} ${cartProvider.itemCount == 1 ? 'producto' : 'productos'}',
            style: TextStyle(
              color: Colors.grey[600],
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyCart() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.shopping_cart_outlined,
            size: 80,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 16),
          const Text(
            'Tu carrito está vacío',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Agrega productos para continuar',
            style: TextStyle(color: Colors.grey[600]),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () => context.go('/'),
            icon: const Icon(Icons.shopping_bag_outlined),
            label: const Text('Ir a comprar'),
          ),
        ],
      ),
    );
  }
}
