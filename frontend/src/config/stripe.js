// frontend/src/config/stripe.js
// Configuración de Stripe
// IMPORTANTE: La clave pública es segura para usar en el frontend
export const STRIPE_PUBLIC_KEY = import.meta.env.VITE_STRIPE_PUBLIC_KEY || 'pk_test_51N1b3XSFq2Y7b1KX9jz3YkYJ4qT6v3Z8fX1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7';

// Para producción, agrega la clave en un archivo .env
// VITE_STRIPE_PUBLIC_KEY=pk_live_tu_clave_real
