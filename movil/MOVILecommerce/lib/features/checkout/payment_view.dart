import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_stripe/flutter_stripe.dart' hide Card;
import '../../data/repositories/checkout_service.dart';
import '../../data/models/pedido.dart';

/// Vista para procesar el pago de un pedido pendiente
class PaymentView extends StatefulWidget {
  final Pedido pedido;

  const PaymentView({
    super.key,
    required this.pedido,
  });

  @override
  State<PaymentView> createState() => _PaymentViewState();
}

class _PaymentViewState extends State<PaymentView> {
  final _checkoutService = CheckoutService();
  bool _isProcessing = false;

  Future<void> _procesarPago() async {
    setState(() {
      _isProcessing = true;
    });

    try {
      // 1. Crear payment intent en el backend
      final paymentData = await _checkoutService.crearPaymentIntent(
        pedidoId: widget.pedido.id,
      );

      final clientSecret = paymentData['client_secret'];
      final paymentIntentId = paymentData['payment_intent_id'];

      if (clientSecret == null) {
        throw Exception('No se recibió el client_secret del servidor');
      }

      // 2. Inicializar Payment Sheet
      await Stripe.instance.initPaymentSheet(
        paymentSheetParameters: SetupPaymentSheetParameters(
          paymentIntentClientSecret: clientSecret,
          merchantDisplayName: 'Movil Ecommerce',
          style: ThemeMode.system,
        ),
      );

      // 3. Presentar Payment Sheet
      await Stripe.instance.presentPaymentSheet();

      // 4. Verificar el estado del pago en el backend
      // Esto es importante según la documentación de Stripe
      if (mounted && paymentIntentId != null) {
        try {
          final verificacion = await _checkoutService.verificarEstadoPago(
            paymentIntentId: paymentIntentId,
          );

          final status = verificacion['status'];

          if (status == 'succeeded') {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('✓ Pago confirmado exitosamente'),
                backgroundColor: Colors.green,
                duration: Duration(seconds: 3),
              ),
            );
          } else {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('⚠ Pago completado. Estado: $status'),
                backgroundColor: Colors.orange,
                duration: Duration(seconds: 3),
              ),
            );
          }
        } catch (e) {
          // Si la verificación falla, igual mostrar éxito porque Stripe confirmó el pago
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('✓ Pago procesado (verificación pendiente)'),
              backgroundColor: Colors.green,
              duration: Duration(seconds: 3),
            ),
          );
        }

        context.go('/profile');
      } else if (mounted) {
        // Si no hay paymentIntentId, asumir éxito
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('✓ Pago procesado exitosamente'),
            backgroundColor: Colors.green,
            duration: Duration(seconds: 3),
          ),
        );
        context.go('/profile');
      }
    } on StripeException catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
                'Pago cancelado: ${e.error.localizedMessage ?? "Error desconocido"}'),
            backgroundColor: Colors.orange,
          ),
        );
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
    return Scaffold(
      appBar: AppBar(
        title: const Text('Procesar Pago'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Información del pedido
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'Pedido #${widget.pedido.codigo}',
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        _buildStatusBadge(widget.pedido.estado),
                      ],
                    ),
                    const SizedBox(height: 16),
                    _buildInfoRow(
                      'Fecha',
                      widget.pedido.fechaCreacion != null
                          ? _formatDate(widget.pedido.fechaCreacion!)
                          : 'N/A',
                    ),
                    _buildInfoRow(
                      'Método de pago',
                      widget.pedido.metodoPago.toUpperCase(),
                    ),
                    _buildInfoRow(
                      'Dirección de envío',
                      widget.pedido.direccionEnvio ?? 'No especificada',
                    ),
                    if (widget.pedido.comentario != null &&
                        widget.pedido.comentario!.isNotEmpty)
                      _buildInfoRow(
                        'Comentarios',
                        widget.pedido.comentario!,
                      ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Detalles de productos
            const Text(
              'Productos',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Card(
              child: ListView.separated(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: widget.pedido.detalles.length,
                separatorBuilder: (_, __) => const Divider(),
                itemBuilder: (context, index) {
                  final detalle = widget.pedido.detalles[index];
                  return ListTile(
                    title: Text(detalle.nombreProducto),
                    subtitle: Text('Cantidad: ${detalle.cantidad}'),
                    trailing: Text(
                      '\$${detalle.subtotalDouble.toStringAsFixed(2)}',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                  );
                },
              ),
            ),
            const SizedBox(height: 16),

            // Resumen de totales
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    _buildTotalRow('Subtotal', widget.pedido.subtotalDouble),
                    _buildTotalRow('Impuestos', widget.pedido.impuestosDouble),
                    const Divider(height: 24),
                    _buildTotalRow(
                      'Total',
                      widget.pedido.totalDouble,
                      isTotal: true,
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Información de pago
            if (widget.pedido.metodoPago == 'tarjeta') ...[
              const Text(
                'Método de pago',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: [
                      const Icon(
                        Icons.credit_card,
                        size: 48,
                        color: Colors.blue,
                      ),
                      const SizedBox(height: 12),
                      const Text(
                        'Pago con tarjeta',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Total a pagar: \$${widget.pedido.totalDouble.toStringAsFixed(2)}',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Theme.of(context).primaryColor,
                        ),
                      ),
                      const SizedBox(height: 16),
                      const Text(
                        '🔒 Tu pago es seguro con Stripe',
                        style: TextStyle(color: Colors.grey),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),

              // Botón de pagar
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _isProcessing ? null : _procesarPago,
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
                          'Pagar \$${widget.pedido.totalDouble.toStringAsFixed(2)}',
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                ),
              ),
            ] else ...[
              // Pedido con pago en efectivo
              Card(
                color: Colors.orange[50],
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    children: [
                      Icon(Icons.money, size: 48, color: Colors.orange[700]),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Pago en efectivo',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'Pagarás \$${widget.pedido.totalDouble.toStringAsFixed(2)} al recibir tu pedido',
                              style: const TextStyle(fontSize: 14),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildStatusBadge(String estado) {
    Color color;
    String text;

    switch (estado.toLowerCase()) {
      case 'pendiente':
        color = Colors.orange;
        text = 'Pendiente';
        break;
      case 'pagado':
        color = Colors.green;
        text = 'Pagado';
        break;
      case 'enviado':
        color = Colors.blue;
        text = 'Enviado';
        break;
      case 'entregado':
        color = Colors.green;
        text = 'Entregado';
        break;
      case 'cancelado':
        color = Colors.red;
        text = 'Cancelado';
        break;
      default:
        color = Colors.grey;
        text = estado;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color),
      ),
      child: Text(
        text,
        style: TextStyle(
          color: color,
          fontWeight: FontWeight.bold,
          fontSize: 12,
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              label,
              style: const TextStyle(
                color: Colors.grey,
                fontSize: 14,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(
                fontWeight: FontWeight.w500,
                fontSize: 14,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTotalRow(String label, double amount, {bool isTotal = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TextStyle(
              fontSize: isTotal ? 18 : 14,
              fontWeight: isTotal ? FontWeight.bold : FontWeight.normal,
            ),
          ),
          Text(
            '\$${amount.toStringAsFixed(2)}',
            style: TextStyle(
              fontSize: isTotal ? 18 : 14,
              fontWeight: isTotal ? FontWeight.bold : FontWeight.normal,
              color: isTotal ? Theme.of(context).primaryColor : null,
            ),
          ),
        ],
      ),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year} ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
  }
}
