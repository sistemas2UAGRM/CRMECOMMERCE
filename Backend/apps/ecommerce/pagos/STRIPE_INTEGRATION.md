# Integración de Pagos con Stripe

## Flujo de Pago Completo

### 1. Crear Pedido desde Carrito
**Endpoint:** `POST /api/ecommerce/carritos/crear-pedido/`

```json
{
  "metodo_pago": "stripe",
  "direccion_envio": "Calle ejemplo 123",
  "comentario": "Entregar por la tarde"
}
```

**Respuesta:**
```json
{
  "pedido_id": 10,
  "codigo": "PED-20250119-0010",
  "total": 150.00,
  "estado": "pendiente"
}
```

### 2. Crear PaymentIntent
**Endpoint:** `POST /api/ecommerce/pagos/crear-payment-intent/`

```json
{
  "pedido_id": 10
}
```

**Respuesta:**
```json
{
  "client_secret": "pi_xxx_secret_yyy",
  "pedido_id": 10,
  "pedido_codigo": "PED-20250119-0010",
  "monto": 150.00,
  "moneda": "usd",
  "payment_intent_id": "pi_xxxxx"
}
```

### 3. Confirmar Pago en el Cliente (Mobile/Frontend)

Usando Stripe SDK en tu aplicación móvil:

```javascript
// React Native / Mobile
const { error, paymentIntent } = await stripe.confirmCardPayment(
  clientSecret,
  {
    paymentMethod: {
      card: cardElement,
      billing_details: {
        name: 'Usuario Ejemplo',
      },
    },
  }
);

if (error) {
  // Mostrar error al usuario
  console.error(error.message);
} else if (paymentIntent.status === 'succeeded') {
  // El pago fue exitoso
  // IMPORTANTE: Llamar al siguiente endpoint para actualizar el pedido
  verificarEstadoPago(paymentIntent.id);
}
```

### 4. Verificar Estado del Pago (DESPUÉS de la confirmación)

**Endpoint:** `POST /api/ecommerce/pagos/verificar-estado-pago/`

**Documentación oficial:** https://docs.stripe.com/payments/payment-intents/verifying-status

```json
{
  "payment_intent_id": "pi_xxxxx"
}
```

**Respuesta exitosa:**
```json
{
  "status": "succeeded",
  "pedido_id": 10,
  "pedido_codigo": "PED-20250119-0010",
  "pedido_estado": "pagado",
  "pagado": true,
  "mensaje": "Pago confirmado exitosamente"
}
```

**Posibles estados:**
- `succeeded`: Pago exitoso, pedido actualizado
- `processing`: Pago en proceso
- `requires_payment_method`: Se requiere otro método de pago

---

## ¿Por qué este flujo?

Según la documentación oficial de Stripe:

> **"Don't attempt to handle order fulfillment on the client side because customers can leave the page after payment is complete but before the fulfillment process initiates."**

Fuente: https://docs.stripe.com/payments/payment-intents/verifying-status

### Soluciones Recomendadas por Stripe:

1. **Webhooks (Producción):** Stripe envía eventos automáticamente a tu servidor
2. **Verificación Manual (Desarrollo/Mobile):** El cliente consulta el estado después de la confirmación

Este proyecto implementa **AMBAS** soluciones:

- **`verificar-estado-pago/`**: Para aplicaciones móviles (recomendado para desarrollo)
- **`webhooks/stripe/`**: Para eventos automáticos de Stripe (producción)

---

## Configuración de Webhooks

### Para Desarrollo Local (Stripe CLI)

1. Instalar Stripe CLI: https://docs.stripe.com/stripe-cli

2. Iniciar sesión:
```bash
stripe login
```

3. Escuchar eventos localmente:
```bash
stripe listen --forward-to http://localhost:8000/api/ecommerce/pagos/webhooks/stripe/
```

4. El comando anterior te dará un `webhook signing secret` (ejemplo: `whsec_xxx`)

5. Agregar el secret a tu archivo `.env`:
```env
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
```

6. En otra terminal, disparar un evento de prueba:
```bash
stripe trigger payment_intent.succeeded
```

### Para Producción

1. Ir al Dashboard de Stripe: https://dashboard.stripe.com/webhooks

2. Crear un nuevo endpoint:
   - URL: `https://tudominio.com/api/ecommerce/pagos/webhooks/stripe/`
   - Eventos a escuchar: `payment_intent.succeeded`, `payment_intent.payment_failed`

3. Copiar el `Signing secret` y agregarlo a tus variables de entorno en producción

4. El webhook se ejecutará automáticamente cuando un pago sea exitoso

---

## Flujo Completo en Diagrama

```
┌─────────────┐
│   Cliente   │
│   (Mobile)  │
└──────┬──────┘
       │
       │ 1. POST /carritos/crear-pedido/
       ▼
┌─────────────────────┐
│  Backend Django     │  → Crea Pedido (estado: pendiente)
│  (Carrito → Pedido) │  → Reserva stock
└──────┬──────────────┘
       │
       │ pedido_id
       ▼
┌─────────────┐
│   Cliente   │
└──────┬──────┘
       │
       │ 2. POST /pagos/crear-payment-intent/
       ▼
┌─────────────────────┐
│  Backend Django     │  → Crea PaymentIntent en Stripe
│                     │  → Guarda Pago (estado: pendiente)
└──────┬──────────────┘
       │
       │ client_secret
       ▼
┌─────────────┐
│   Cliente   │  → 3. Confirma pago con Stripe SDK
│   (Mobile)  │     stripe.confirmCardPayment(client_secret)
└──────┬──────┘
       │
       │ ✅ payment_intent.status === 'succeeded'
       │
       │ 4. POST /pagos/verificar-estado-pago/
       ▼
┌─────────────────────┐
│  Backend Django     │  → Consulta PaymentIntent en Stripe
│                     │  → Actualiza Pedido (estado: pagado)
│                     │  → Actualiza Pago (estado: exitoso)
│                     │  → Deduce stock (reservado → vendido)
│                     │  → Crea movimiento de stock
└─────────────────────┘
```

---

## Qué hace cada Endpoint

### `verificar-estado-pago/` (Nuevo - RECOMENDADO para Mobile)
- **Cuándo:** Después de que el cliente confirme el pago con Stripe SDK
- **Qué hace:**
  1. Consulta el estado del PaymentIntent directamente en Stripe
  2. Si está `succeeded`, actualiza el pedido a "pagado"
  3. Deduce el stock
  4. Retorna confirmación al cliente
- **Ventaja:** No depende de webhooks, funciona en desarrollo sin configuración adicional

### `webhooks/stripe/` (Automático - Para Producción)
- **Cuándo:** Stripe lo llama automáticamente cuando un evento ocurre
- **Qué hace:** Lo mismo que `verificar-estado-pago/` pero de forma automática
- **Requisito:** Configurar webhook en Dashboard de Stripe y tener `STRIPE_WEBHOOK_SECRET`

**Nota:** Ambos endpoints verifican si el pedido ya fue actualizado para evitar duplicados.

---

## Tarjetas de Prueba

### Pago Exitoso
```
Número: 4242 4242 4242 4242
Fecha: Cualquier fecha futura (ej: 12/25)
CVC: Cualquier 3 dígitos (ej: 123)
ZIP: Cualquier código postal
```

### Requiere Autenticación 3D Secure
```
Número: 4000 0025 0000 3155
```

### Pago Fallido
```
Número: 4000 0000 0000 9995
```

Más tarjetas de prueba: https://docs.stripe.com/testing

---

## Variables de Entorno Requeridas

En tu archivo `.env`:

```env
# Stripe Keys (obtener de https://dashboard.stripe.com/apikeys)
STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxxxxxxx  # Solo para webhooks
```

---

## Ejemplo de Integración en React Native

```javascript
import { useStripe } from '@stripe/stripe-react-native';

const PaymentScreen = ({ pedidoId }) => {
  const { confirmPayment } = useStripe();
  
  const handlePago = async () => {
    try {
      // 1. Crear PaymentIntent
      const response = await fetch('http://tu-backend/api/ecommerce/pagos/crear-payment-intent/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ pedido_id: pedidoId })
      });
      
      const { client_secret, payment_intent_id } = await response.json();
      
      // 2. Confirmar pago con Stripe
      const { error, paymentIntent } = await confirmPayment(client_secret, {
        paymentMethodType: 'Card',
      });
      
      if (error) {
        Alert.alert('Error', error.message);
        return;
      }
      
      // 3. Verificar estado del pago en el backend
      if (paymentIntent.status === 'Succeeded') {
        const verificacion = await fetch('http://tu-backend/api/ecommerce/pagos/verificar-estado-pago/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ payment_intent_id })
        });
        
        const resultado = await verificacion.json();
        
        if (resultado.status === 'succeeded') {
          Alert.alert('¡Éxito!', 'Tu pago fue procesado correctamente');
          navigation.navigate('OrderSuccess', { pedidoId: resultado.pedido_id });
        }
      }
      
    } catch (error) {
      console.error('Error en el pago:', error);
      Alert.alert('Error', 'Ocurrió un error al procesar el pago');
    }
  };
  
  return (
    <View>
      <Button title="Pagar" onPress={handlePago} />
    </View>
  );
};
```

---

## Documentación Oficial de Stripe

- **Payment Intents:** https://docs.stripe.com/payments/payment-intents
- **Verificar Estado de Pagos:** https://docs.stripe.com/payments/payment-intents/verifying-status
- **Webhooks:** https://docs.stripe.com/webhooks
- **Testing:** https://docs.stripe.com/testing
- **Stripe CLI:** https://docs.stripe.com/stripe-cli
