// frontend/src/modulos/usuarios/clientes/components/ModalPago.jsx
import React, { useState } from 'react';
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';
import { loadStripe } from '@stripe/stripe-js';
import { STRIPE_PUBLIC_KEY } from '../../../../config/stripe';
import pagosService from '../../../../services/pagosService';

const stripePromise = loadStripe(STRIPE_PUBLIC_KEY);

const CheckoutForm = ({ pedido, onSuccess, onCancel }) => {
    const stripe = useStripe();
    const elements = useElements();
    const [processing, setProcessing] = useState(false);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!stripe || !elements) {
            return;
        }

        setProcessing(true);
        setError(null);

        try {
            // Obtener el clientSecret del backend
            const { clientSecret } = await pagosService.iniciarPago(pedido.id);

            // Confirmar el pago con Stripe
            const { error: stripeError, paymentIntent } = await stripe.confirmCardPayment(clientSecret, {
                payment_method: {
                    card: elements.getElement(CardElement),
                    billing_details: {
                        name: pedido.cliente_username || 'Cliente',
                        email: pedido.cliente_email || '',
                    },
                },
            });

            if (stripeError) {
                setError(stripeError.message);
                setProcessing(false);
                return;
            }

            if (paymentIntent.status === 'succeeded') {
                // Marcar el pedido como pagado en el backend
                await pagosService.confirmarPago(pedido.id);
                onSuccess();
            }
        } catch (err) {
            setError(err.response?.data?.error || 'Error al procesar el pago');
            setProcessing(false);
        }
    };

    const cardElementOptions = {
        style: {
            base: {
                fontSize: '16px',
                color: '#424770',
                '::placeholder': {
                    color: '#aab7c4',
                },
            },
            invalid: {
                color: '#9e2146',
            },
        },
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Información de la tarjeta
                </label>
                <div className="border border-gray-300 rounded-md p-3 bg-white">
                    <CardElement options={cardElementOptions} />
                </div>
            </div>

            {error && (
                <div className="bg-red-50 border border-red-200 rounded-md p-3">
                    <p className="text-sm text-red-600">{error}</p>
                </div>
            )}

            <div className="bg-gray-50 border border-gray-200 rounded-md p-4">
                <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-gray-600">Subtotal:</span>
                    <span className="text-sm font-medium text-gray-900">
                        ${pedido.subtotal ? parseFloat(pedido.subtotal).toFixed(2) : '0.00'}
                    </span>
                </div>
                <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-gray-600">Impuestos:</span>
                    <span className="text-sm font-medium text-gray-900">
                        ${pedido.impuestos ? parseFloat(pedido.impuestos).toFixed(2) : '0.00'}
                    </span>
                </div>
                <div className="flex justify-between items-center pt-2 border-t border-gray-300">
                    <span className="text-base font-semibold text-gray-900">Total a pagar:</span>
                    <span className="text-xl font-bold text-indigo-600">
                        ${pedido.total ? parseFloat(pedido.total).toFixed(2) : '0.00'}
                    </span>
                </div>
            </div>

            <div className="flex gap-3">
                <button
                    type="button"
                    onClick={onCancel}
                    className="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500"
                    disabled={processing}
                >
                    Cancelar
                </button>
                <button
                    type="submit"
                    disabled={!stripe || processing}
                    className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                    {processing ? (
                        <>
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                            Procesando...
                        </>
                    ) : (
                        `Pagar $${pedido.total ? parseFloat(pedido.total).toFixed(2) : '0.00'}`
                    )}
                </button>
            </div>
        </form>
    );
};

const ModalPago = ({ pedido, onClose, onSuccess }) => {
    return (
        <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-md w-full p-6">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-2xl font-bold text-gray-900">Pagar Pedido</h2>
                    <button
                        onClick={onClose}
                        className="text-gray-500 hover:text-gray-800 focus:outline-none"
                    >
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                <div className="mb-4">
                    <p className="text-sm text-gray-600">
                        Pedido: <span className="font-medium text-gray-900">#{pedido.codigo || pedido.id}</span>
                    </p>
                </div>

                <Elements stripe={stripePromise}>
                    <CheckoutForm
                        pedido={pedido}
                        onSuccess={onSuccess}
                        onCancel={onClose}
                    />
                </Elements>
            </div>
        </div>
    );
};

export default ModalPago;
