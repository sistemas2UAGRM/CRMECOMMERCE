// Vista del Carrito de Compras
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import carritoService from '../../../../services/carritosService';

export default function Carrito() {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [direccionEnvio, setDireccionEnvio] = useState('');
    const [showDireccionModal, setShowDireccionModal] = useState(false);
    const [creandoPedido, setCreandoPedido] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchCarrito = async () => {
            try {
                setLoading(true);
                const data = await carritoService.obtenerMiCarrito();
                setItems(data.items || []);
                setError(null);
            } catch (err) {
                setError("No se pudo cargar el carrito. Intenta de nuevo más tarde.");
                console.error("Error fetching carrito:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchCarrito();
    }, []);

    const eliminarItem = async (id) => {
        try {
            await carritoService.eliminarItem(id);
            setItems(items.filter(item => item.id !== id));
        } catch (err) {
            console.error("Error eliminando item del carrito:", err);
            alert("Error al eliminar el producto del carrito.");
        }
    };

    const confirmarPedido = () => {
        if (items.length === 0) {
            alert("El carrito está vacío.");
            return;
        }
        setShowDireccionModal(true);
    };

    const crearPedido = async () => {
        if (!direccionEnvio.trim()) {
            alert("Por favor ingresa una dirección de envío.");
            return;
        }

        try {
            setCreandoPedido(true);
            const pedido = await carritoService.crearPedidoDesdeCarrito(direccionEnvio);
            alert(`¡Pedido creado exitosamente! Código: ${pedido.codigo || pedido.id}`);
            setItems([]);
            setShowDireccionModal(false);
            setDireccionEnvio('');
            // Navegar a la vista de pedidos
            navigate('/cliente/ordenes');
        } catch (err) {
            console.error("Error creando pedido:", err);
            const errorMsg = err.response?.data?.error || "Hubo un error al crear el pedido. Verifica el stock disponible.";
            alert(errorMsg);
        } finally {
            setCreandoPedido(false);
        }
    };

    const actualizarCantidad = async (itemId, productoId, nuevaCantidad) => {
        if (nuevaCantidad < 1) return;

        try {
            // Agregar item actualiza la cantidad en el backend
            await carritoService.agregarItem(productoId, nuevaCantidad);

            // Recargar el carrito para obtener los datos actualizados
            const data = await carritoService.obtenerMiCarrito();
            setItems(data.items || []);
        } catch (err) {
            console.error("Error actualizando la cantidad del item:", err);
            alert("Error al actualizar la cantidad. Verifica el stock disponible.");
        }
    };

    const calcularTotal = () => {
        return items.reduce((total, item) => {
            return total + (parseFloat(item.precio_capturado || item.producto.precio) * item.cantidad);
        }, 0);
    };

    if (loading) return <div className="text-center py-12 text-gray-500">Cargando carrito...</div>;
    if (error) return <div className="text-center py-12 text-red-600 bg-red-50 p-4 rounded-md">{error}</div>;

    return (
        <div className="p-6 max-w-6xl mx-auto">
            <h1 className="text-3xl font-bold tracking-tight text-gray-900 mb-8">Carrito de Compras</h1>

            {items.length > 0 ? (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Lista de items */}
                    <div className="lg:col-span-2 space-y-4">
                        {items.map(item => (
                            <div key={item.id} className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow">
                                <div className="flex gap-4">
                                    <img
                                        src={item.producto.imagen_principal_url || 'https://via.placeholder.com/100'}
                                        alt={item.producto.nombre}
                                        className="w-24 h-24 object-cover rounded-md flex-shrink-0"
                                    />
                                    <div className="flex-1">
                                        <div className="flex justify-between items-start">
                                            <div>
                                                <h3 className="text-lg font-semibold text-gray-800">{item.producto.nombre}</h3>
                                                <p className="text-sm text-gray-500 mt-1">SKU: {item.producto.codigo}</p>
                                            </div>
                                            <button
                                                onClick={() => eliminarItem(item.id)}
                                                className="text-red-600 hover:text-red-800 p-1"
                                                title="Eliminar del carrito"
                                            >
                                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                                </svg>
                                            </button>
                                        </div>

                                        <div className="flex items-center justify-between mt-4">
                                            <div className="flex items-center gap-3">
                                                <span className="text-sm text-gray-600">Cantidad:</span>
                                                <div className="flex items-center border border-gray-300 rounded-md">
                                                    <button
                                                        onClick={() => actualizarCantidad(item.id, item.producto.id, item.cantidad - 1)}
                                                        className="px-3 py-1 text-gray-600 hover:bg-gray-100 rounded-l-md"
                                                        disabled={item.cantidad <= 1}
                                                    >
                                                        -
                                                    </button>
                                                    <span className="px-4 py-1 text-gray-800 font-medium">{item.cantidad}</span>
                                                    <button
                                                        onClick={() => actualizarCantidad(item.id, item.producto.id, item.cantidad + 1)}
                                                        className="px-3 py-1 text-gray-600 hover:bg-gray-100 rounded-r-md"
                                                    >
                                                        +
                                                    </button>
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <p className="text-sm text-gray-500">Precio unitario: ${parseFloat(item.precio_capturado || item.producto.precio).toFixed(2)}</p>
                                                <p className="text-lg font-bold text-gray-900">
                                                    ${(parseFloat(item.precio_capturado || item.producto.precio) * item.cantidad).toFixed(2)}
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Resumen del pedido */}
                    <div className="lg:col-span-1">
                        <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm sticky top-6">
                            <h2 className="text-xl font-bold text-gray-900 mb-4">Resumen del pedido</h2>

                            <div className="space-y-3 mb-6">
                                <div className="flex justify-between text-gray-600">
                                    <span>Subtotal ({items.length} {items.length === 1 ? 'producto' : 'productos'})</span>
                                    <span>${calcularTotal().toFixed(2)}</span>
                                </div>
                                <div className="flex justify-between text-gray-600">
                                    <span>Envío</span>
                                    <span>A calcular</span>
                                </div>
                                <div className="border-t border-gray-200 pt-3 flex justify-between text-lg font-bold text-gray-900">
                                    <span>Total</span>
                                    <span>${calcularTotal().toFixed(2)}</span>
                                </div>
                            </div>

                            <button
                                onClick={confirmarPedido}
                                className="w-full px-6 py-3 bg-indigo-600 text-white text-sm font-medium rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
                            >
                                Proceder al Pago
                            </button>

                            <button
                                onClick={() => navigate('/cliente/productos')}
                                className="w-full mt-3 px-6 py-3 bg-white text-indigo-600 text-sm font-medium rounded-md border border-indigo-600 hover:bg-indigo-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
                            >
                                Continuar Comprando
                            </button>
                        </div>
                    </div>
                </div>
            ) : (
                <div className="text-center py-12">
                    <svg className="mx-auto h-24 w-24 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                    </svg>
                    <h3 className="mt-4 text-lg font-medium text-gray-900">Tu carrito está vacío</h3>
                    <p className="mt-2 text-sm text-gray-500">Comienza a agregar productos para realizar tu compra.</p>
                    <button
                        onClick={() => navigate('/cliente/productos')}
                        className="mt-6 px-6 py-3 bg-indigo-600 text-white text-sm font-medium rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                        Ver Productos
                    </button>
                </div>
            )}

            {/* Modal para dirección de envío */}
            {showDireccionModal && (
                <div className="fixed inset-0  bg-opacity-50 flex items-center justify-center z-50 p-4" style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)' }}>
                    <div className="bg-white rounded-lg max-w-md w-full p-6">
                        <h2 className="text-2xl font-bold text-gray-900 mb-4">Dirección de Envío</h2>
                        <p className="text-sm text-gray-600 mb-4">Por favor ingresa la dirección donde deseas recibir tu pedido.</p>

                        <textarea
                            value={direccionEnvio}
                            onChange={(e) => setDireccionEnvio(e.target.value)}
                            placeholder="Calle, número, ciudad, código postal..."
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 min-h-24"
                            rows={4}
                        />

                        <div className="flex gap-3 mt-6">
                            <button
                                onClick={() => {
                                    setShowDireccionModal(false);
                                    setDireccionEnvio('');
                                }}
                                className="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500"
                                disabled={creandoPedido}
                            >
                                Cancelar
                            </button>
                            <button
                                onClick={crearPedido}
                                disabled={creandoPedido || !direccionEnvio.trim()}
                                className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
                            >
                                {creandoPedido ? 'Creando...' : 'Confirmar Pedido'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}