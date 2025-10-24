import React, { useState, useEffect } from 'react';
import pedidosService from '../../../../services/pedidosService';
import ModalPago from './ModalPago';

export default function Ordenes() {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedOrder, setSelectedOrder] = useState(null);
    const [pedidoAPagar, setPedidoAPagar] = useState(null);

    useEffect(() => {
        fetchOrders();
    }, []);

    const fetchOrders = async () => {
        try {
            setLoading(true);
            const data = await pedidosService.listarPedidosUsuario();
            console.log('=== DEBUG PEDIDOS ===');
            console.log('Respuesta completa:', data);
            console.log('Tipo de data:', typeof data);
            console.log('Es array?:', Array.isArray(data));
            console.log('data.results:', data.results);
            console.log('data.length:', data.length);
            console.log('=====================');

            // Intentar extraer los pedidos de diferentes formas
            let pedidos = [];
            if (Array.isArray(data)) {
                pedidos = data;
            } else if (data.results && Array.isArray(data.results)) {
                pedidos = data.results;
            } else if (data.data && Array.isArray(data.data)) {
                pedidos = data.data;
            }

            console.log('Pedidos extraídos:', pedidos);
            setOrders(pedidos);
            setError(null);
        } catch (err) {
            setError("No se pudieron cargar los pedidos. Intenta de nuevo más tarde.");
            console.error("Error completo fetching orders:", err);
            console.error("Error response:", err.response);
        } finally {
            setLoading(false);
        }
    };

    const getEstadoBadge = (estado) => {
        const badges = {
            'pendiente': 'bg-yellow-100 text-yellow-800',
            'pagado': 'bg-green-100 text-green-800',
            'enviado': 'bg-blue-100 text-blue-800',
            'entregado': 'bg-purple-100 text-purple-800',
            'cancelado': 'bg-red-100 text-red-800'
        };
        return badges[estado] || 'bg-gray-100 text-gray-800';
    };

    const getEstadoTexto = (estado) => {
        const textos = {
            'pendiente': 'Pendiente',
            'pagado': 'Pagado',
            'enviado': 'Enviado',
            'entregado': 'Entregado',
            'cancelado': 'Cancelado'
        };
        return textos[estado] || estado;
    };

    const handlePagar = (pedido) => {
        setPedidoAPagar(pedido);
    };

    const handlePagoExitoso = () => {
        setPedidoAPagar(null);
        fetchOrders(); // Recargar los pedidos
        alert('¡Pago realizado exitosamente!');
    };

    const handleCerrarModal = () => {
        setPedidoAPagar(null);
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-center py-12">
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 max-w-md mx-auto">
                    <svg className="mx-auto h-12 w-12 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p className="mt-2 text-red-600">{error}</p>
                    <button
                        onClick={fetchOrders}
                        className="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                    >
                        Reintentar
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <div className="mb-8">
                <h1 className="text-3xl font-bold tracking-tight text-gray-900">Mis Pedidos</h1>
                <p className="mt-2 text-sm text-gray-600">
                    Gestiona y revisa todos tus pedidos realizados
                </p>
            </div>

            {orders.length > 0 ? (
                <div className="space-y-4">
                    {orders.map(order => (
                        <div
                            key={order.id}
                            className="bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow overflow-hidden"
                        >
                            <div className="p-6">
                                <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
                                    <div className="flex items-center gap-4">
                                        <div>
                                            <h3 className="text-lg font-semibold text-gray-900">
                                                Pedido #{order.codigo || order.id}
                                            </h3>
                                            <p className="text-sm text-gray-500 mt-1">
                                                {order.fecha_creacion
                                                    ? new Date(order.fecha_creacion).toLocaleDateString('es-ES', {
                                                        year: 'numeric',
                                                        month: 'long',
                                                        day: 'numeric',
                                                        hour: '2-digit',
                                                        minute: '2-digit'
                                                    })
                                                    : 'Fecha no disponible'
                                                }
                                            </p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getEstadoBadge(order.estado)}`}>
                                            {getEstadoTexto(order.estado)}
                                        </span>
                                    </div>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                                    <div className="bg-gray-50 p-4 rounded-md">
                                        <p className="text-xs text-gray-500 mb-1">Subtotal</p>
                                        <p className="text-lg font-semibold text-gray-900">
                                            ${order.subtotal ? parseFloat(order.subtotal).toFixed(2) : '0.00'}
                                        </p>
                                    </div>
                                    <div className="bg-gray-50 p-4 rounded-md">
                                        <p className="text-xs text-gray-500 mb-1">Impuestos</p>
                                        <p className="text-lg font-semibold text-gray-900">
                                            ${order.impuestos ? parseFloat(order.impuestos).toFixed(2) : '0.00'}
                                        </p>
                                    </div>
                                    <div className="bg-indigo-50 p-4 rounded-md">
                                        <p className="text-xs text-indigo-600 mb-1">Total</p>
                                        <p className="text-xl font-bold text-indigo-600">
                                            ${order.total ? parseFloat(order.total).toFixed(2) : '0.00'}
                                        </p>
                                    </div>
                                </div>

                                {order.direccion_envio && (
                                    <div className="mb-4">
                                        <p className="text-xs text-gray-500 mb-1">Dirección de Envío</p>
                                        <p className="text-sm text-gray-700">{order.direccion_envio}</p>
                                    </div>
                                )}

                                {order.detalles && order.detalles.length > 0 && (
                                    <div className="mt-4">
                                        <button
                                            onClick={() => setSelectedOrder(selectedOrder === order.id ? null : order.id)}
                                            className="text-sm text-indigo-600 hover:text-indigo-800 font-medium flex items-center gap-2"
                                        >
                                            {selectedOrder === order.id ? 'Ocultar' : 'Ver'} detalles ({order.detalles.length} {order.detalles.length === 1 ? 'producto' : 'productos'})
                                            <svg
                                                className={`w-4 h-4 transition-transform ${selectedOrder === order.id ? 'rotate-180' : ''}`}
                                                fill="none"
                                                stroke="currentColor"
                                                viewBox="0 0 24 24"
                                            >
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                            </svg>
                                        </button>

                                        {selectedOrder === order.id && (
                                            <div className="mt-4 border-t border-gray-200 pt-4">
                                                <h4 className="text-sm font-semibold text-gray-900 mb-3">Productos</h4>
                                                <div className="space-y-3">
                                                    {order.detalles.map((detalle, index) => (
                                                        <div key={index} className="flex items-center gap-4 bg-gray-50 p-3 rounded-md">
                                                            <div className="flex-1">
                                                                <p className="text-sm font-medium text-gray-900">{detalle.nombre_producto}</p>
                                                                <p className="text-xs text-gray-500 mt-1">
                                                                    Cantidad: {detalle.cantidad} × ${parseFloat(detalle.precio_unitario).toFixed(2)}
                                                                </p>
                                                            </div>
                                                            <p className="text-sm font-semibold text-gray-900">
                                                                ${parseFloat(detalle.subtotal).toFixed(2)}
                                                            </p>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )}

                                {order.comentario && (
                                    <div className="mt-4 bg-blue-50 border border-blue-200 rounded-md p-3">
                                        <p className="text-xs text-blue-600 mb-1">Comentario</p>
                                        <p className="text-sm text-blue-900">{order.comentario}</p>
                                    </div>
                                )}

                                {/* Botón de pagar si el pedido está pendiente */}
                                {!order.pagado && order.estado === 'pendiente' && (
                                    <div className="mt-4 pt-4 border-t border-gray-200">
                                        <button
                                            onClick={() => handlePagar(order)}
                                            className="w-full md:w-auto px-6 py-3 bg-green-600 text-white text-sm font-medium rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors flex items-center justify-center gap-2"
                                        >
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                                            </svg>
                                            Pagar ${order.total ? parseFloat(order.total).toFixed(2) : '0.00'}
                                        </button>
                                    </div>
                                )}

                                {order.pagado && (
                                    <div className="mt-4 pt-4 border-t border-gray-200">
                                        <div className="flex items-center gap-2 text-green-600">
                                            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                            </svg>
                                            <span className="text-sm font-medium">Pedido pagado</span>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="text-center py-12">
                    <svg className="mx-auto h-24 w-24 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <h3 className="mt-4 text-lg font-medium text-gray-900">No tienes pedidos</h3>
                    <p className="mt-2 text-sm text-gray-500">Comienza a realizar compras para ver tus pedidos aquí.</p>
                </div>
            )}

            {/* Modal de pago con Stripe */}
            {pedidoAPagar && (
                <ModalPago
                    pedido={pedidoAPagar}
                    onClose={handleCerrarModal}
                    onSuccess={handlePagoExitoso}
                />
            )}
        </div>
    );
}