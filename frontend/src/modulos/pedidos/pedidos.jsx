// src/modulos/pedidos/pedidos.jsx
import React, { useEffect, useState } from 'react';
import {
    Package, Eye, Search as SearchIcon,
    Filter, RefreshCw, User, Calendar, DollarSign,
    AlertCircle, CheckCircle, Clock, X, Edit
} from 'lucide-react';
import pedidosService from '../../services/pedidosService';
import { toast } from 'react-hot-toast';

const ESTADO_PEDIDO = {
    'pendiente': { name: 'Pendiente', color: 'bg-yellow-100 text-yellow-800' },
    'pagado': { name: 'Pagado', color: 'bg-blue-100 text-blue-800' },
    'enviado': { name: 'Enviado', color: 'bg-purple-100 text-purple-800' },
    'entregado': { name: 'Entregado', color: 'bg-green-100 text-green-800' },
    'cancelado': { name: 'Cancelado', color: 'bg-red-100 text-red-800' },
};

export default function GestionPedidos() {
    const [pedidos, setPedidos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [query, setQuery] = useState('');
    const [estadoFilter, setEstadoFilter] = useState('');

    const [showDetailsModal, setShowDetailsModal] = useState(false);
    const [showStatusModal, setShowStatusModal] = useState(false);
    const [currentPedido, setCurrentPedido] = useState(null);
    const [newStatus, setNewStatus] = useState('');

    // Función para obtener pedidos - FIX: Removed double destructuring
    const fetchPedidos = async (searchQuery = '', estadoFilterParam = estadoFilter) => {
        setLoading(true);
        setError(null);
        try {
            const params = {};

            if (searchQuery) {
                params.search = searchQuery;
            }

            if (estadoFilterParam) {
                params.estado = estadoFilterParam;
            }

            // FIX: Service already returns response.data, so no need to destructure
            const data = await pedidosService.listarTodos(params);

            console.log('DEBUG FRONTEND: Response data:', data);
            console.log('DEBUG FRONTEND: Data length:', data?.length);

            setPedidos(data || []);
        } catch (err) {
            console.error('Error al cargar pedidos:', err);
            if (err.response?.status === 403) {
                setError('No tienes permisos para ver los pedidos.');
            } else {
                setError('Error al cargar pedidos.');
            }
        } finally {
            setLoading(false);
        }
    };

    // Cargar pedidos al montar el componente
    useEffect(() => {
        fetchPedidos('', '');
    }, []);

    // Efecto para aplicar filtros automáticamente
    useEffect(() => {
        const timeoutId = setTimeout(() => {
            fetchPedidos(query, estadoFilter);
        }, 300);

        return () => clearTimeout(timeoutId);
    }, [estadoFilter]);

    // Handler para búsqueda
    const handleSearchSubmit = (e) => {
        if (e) e.preventDefault();
        fetchPedidos(query, estadoFilter);
    };

    // Función para ver detalles del pedido
    const verDetalles = async (pedido) => {
        try {
            const data = await pedidosService.obtener(pedido.id);
            setCurrentPedido(data);
            setShowDetailsModal(true);
        } catch (err) {
            console.error('Error al cargar detalles:', err);
            toast.error('Error al cargar detalles del pedido');
        }
    };

    // Función para cambiar estado
    const cambiarEstado = (pedido) => {
        setCurrentPedido(pedido);
        setNewStatus(pedido.estado);
        setShowStatusModal(true);
    };

    // Función para guardar nuevo estado
    const guardarEstado = async () => {
        if (!currentPedido) return;

        try {
            await pedidosService.actualizarEstado(currentPedido.id, newStatus);
            toast.success('Estado del pedido actualizado');
            setShowStatusModal(false);
            fetchPedidos(query, estadoFilter);
        } catch (err) {
            console.error('Error al actualizar estado:', err);
            toast.error('Error al actualizar el estado del pedido');
        }
    };

    // Función para formatear fecha
    const formatearFecha = (fechaString) => {
        if (!fechaString) return 'No especificado';
        return new Date(fechaString).toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    // Función para formatear precio
    const formatearPrecio = (precio) => {
        return new Intl.NumberFormat('es-BO', {
            style: 'currency',
            currency: 'BOB'
        }).format(precio);
    };

    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-[#2e7e8b] rounded-lg">
                                <Package size={24} className="text-white" />
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold text-gray-900">Gestión de Pedidos</h1>
                                <p className="text-gray-600">Administra todos los pedidos del sistema</p>
                            </div>
                        </div>

                        <button
                            onClick={() => fetchPedidos(query, estadoFilter)}
                            disabled={loading}
                            className="inline-flex items-center gap-2 rounded-md bg-gray-100 px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-200 transition disabled:opacity-50"
                        >
                            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
                            Actualizar
                        </button>
                    </div>

                    {/* Filtros y búsqueda */}
                    <div className="flex flex-col md:flex-row gap-4 items-end">
                        {/* Búsqueda */}
                        <div className="flex-1">
                            <label className="block text-sm font-medium text-gray-700 mb-1">Buscar</label>
                            <form onSubmit={handleSearchSubmit} className="relative">
                                <input
                                    value={query}
                                    onChange={(e) => setQuery(e.target.value)}
                                    placeholder="Código, cliente, email..."
                                    className="w-full rounded-md border border-gray-300 px-4 py-2 pl-10 shadow-sm focus:outline-none focus:ring-2 focus:ring-[#2e7e8b] focus:border-[#2e7e8b]"
                                />
                                <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                            </form>
                        </div>

                        {/* Filtro por Estado */}
                        <div className="min-w-[150px]">
                            <label className="block text-sm font-medium text-gray-700 mb-1">Estado</label>
                            <select
                                value={estadoFilter}
                                onChange={(e) => setEstadoFilter(e.target.value)}
                                className="w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-[#2e7e8b] focus:border-[#2e7e8b]"
                            >
                                <option value="">Todos los estados</option>
                                <option value="pendiente">Pendiente</option>
                                <option value="pagado">Pagado</option>
                                <option value="enviado">Enviado</option>
                                <option value="entregado">Entregado</option>
                                <option value="cancelado">Cancelado</option>
                            </select>
                        </div>

                        {/* Botón de búsqueda */}
                        <button
                            onClick={handleSearchSubmit}
                            className="inline-flex items-center gap-2 rounded-md bg-[#2e7e8b] px-4 py-2 text-sm font-semibold text-white shadow-md hover:bg-[#256a76] transition"
                        >
                            <SearchIcon size={16} /> Buscar
                        </button>
                    </div>
                </div>

                {/* Estado de carga */}
                {loading && (
                    <div className="bg-white rounded-lg shadow-sm p-8">
                        <div className="flex items-center justify-center">
                            <RefreshCw className="animate-spin h-8 w-8 text-[#2e7e8b]" />
                            <span className="ml-3 text-gray-600">Cargando pedidos...</span>
                        </div>
                    </div>
                )}

                {/* Error */}
                {error && (
                    <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
                        <div className="flex items-center gap-3 text-red-600">
                            <AlertCircle size={24} />
                            <div>
                                <h3 className="font-semibold">Error al cargar pedidos</h3>
                                <p className="text-sm">{error}</p>
                            </div>
                        </div>
                    </div>
                )}

                {/* Lista de pedidos */}
                {!loading && !error && (
                    <div className="bg-white rounded-lg shadow-sm">
                        {pedidos.length > 0 ? (
                            <div className="overflow-x-auto">
                                <table className="min-w-full divide-y divide-gray-200">
                                    <thead className="bg-gray-50">
                                        <tr>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Código
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Cliente
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Fecha
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Estado
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Total
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Acciones
                                            </th>
                                        </tr>
                                    </thead>
                                    <tbody className="bg-white divide-y divide-gray-200">
                                        {pedidos.map((pedido) => (
                                            <tr key={pedido.id} className="hover:bg-gray-50">
                                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                                    {pedido.codigo}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                    {pedido.cliente ? `${pedido.cliente.username} (${pedido.cliente.email})` : 'Anónimo'}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                    {formatearFecha(pedido.fecha_creacion)}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap">
                                                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${ESTADO_PEDIDO[pedido.estado]?.color || 'bg-gray-100 text-gray-800'}`}>
                                                        {ESTADO_PEDIDO[pedido.estado]?.name || pedido.estado}
                                                    </span>
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                                    {formatearPrecio(pedido.total)}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                                    <div className="flex gap-2">
                                                        <button
                                                            onClick={() => verDetalles(pedido)}
                                                            className="text-[#2e7e8b] hover:text-[#256a76] transition"
                                                            title="Ver detalles"
                                                        >
                                                            <Eye size={16} />
                                                        </button>
                                                        <button
                                                            onClick={() => cambiarEstado(pedido)}
                                                            className="text-blue-600 hover:text-blue-800 transition"
                                                            title="Cambiar estado"
                                                        >
                                                            <Edit size={16} />
                                                        </button>
                                                    </div>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        ) : (
                            <div className="p-8 text-center">
                                <Package size={48} className="mx-auto text-gray-400 mb-4" />
                                <h3 className="text-lg font-medium text-gray-900 mb-2">No hay pedidos</h3>
                                <p className="text-gray-500">No se encontraron pedidos con los filtros aplicados.</p>
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* Modal de detalles */}
            {showDetailsModal && currentPedido && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
                        <div className="p-6">
                            <div className="flex justify-between items-center mb-6">
                                <h2 className="text-2xl font-bold text-gray-900">Detalles del Pedido #{currentPedido.codigo}</h2>
                                <button
                                    onClick={() => setShowDetailsModal(false)}
                                    className="text-gray-400 hover:text-gray-600"
                                >
                                    <X size={24} />
                                </button>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                                <div>
                                    <h3 className="text-lg font-semibold mb-2">Información General</h3>
                                    <p><strong>Cliente:</strong> {currentPedido.cliente ? `${currentPedido.cliente.username} (${currentPedido.cliente.email})` : 'Anónimo'}</p>
                                    <p><strong>Fecha:</strong> {formatearFecha(currentPedido.fecha_creacion)}</p>
                                    <p><strong>Estado:</strong> <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${ESTADO_PEDIDO[currentPedido.estado]?.color || 'bg-gray-100 text-gray-800'}`}>{ESTADO_PEDIDO[currentPedido.estado]?.name || currentPedido.estado}</span></p>
                                    <p><strong>Método de pago:</strong> {currentPedido.metodo_pago || 'No especificado'}</p>
                                    {currentPedido.direccion_envio && <p><strong>Dirección de envío:</strong> {currentPedido.direccion_envio}</p>}
                                    {currentPedido.comentario && <p><strong>Comentario:</strong> {currentPedido.comentario}</p>}
                                </div>
                                <div>
                                    <h3 className="text-lg font-semibold mb-2">Resumen de Precios</h3>
                                    <p><strong>Subtotal:</strong> {formatearPrecio(currentPedido.subtotal)}</p>
                                    <p><strong>Impuestos:</strong> {formatearPrecio(currentPedido.impuestos)}</p>
                                    <p className="text-xl font-bold"><strong>Total:</strong> {formatearPrecio(currentPedido.total)}</p>
                                </div>
                            </div>

                            <div>
                                <h3 className="text-lg font-semibold mb-4">Productos</h3>
                                <div className="space-y-4">
                                    {currentPedido.detalles && currentPedido.detalles.map((detalle) => (
                                        <div key={detalle.id} className="border rounded-md p-4 bg-gray-50">
                                            <div className="flex justify-between items-start">
                                                <div className="flex-1">
                                                    <h4 className="font-semibold text-gray-800">{detalle.nombre_producto}</h4>
                                                    <p className="text-sm text-gray-600">Cantidad: {detalle.cantidad}</p>
                                                    <p className="text-sm text-gray-600">Precio unitario: {formatearPrecio(detalle.precio_unitario)}</p>
                                                    {detalle.descuento > 0 && <p className="text-sm text-red-600">Descuento: -{formatearPrecio(detalle.descuento)}</p>}
                                                </div>
                                                <div className="text-right">
                                                    <p className="font-semibold text-gray-900">{formatearPrecio(detalle.subtotal)}</p>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Modal de cambiar estado */}
            {showStatusModal && currentPedido && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                    <div className="bg-white rounded-lg max-w-md w-full">
                        <div className="p-6">
                            <div className="flex justify-between items-center mb-4">
                                <h2 className="text-xl font-bold text-gray-900">Cambiar Estado del Pedido</h2>
                                <button
                                    onClick={() => setShowStatusModal(false)}
                                    className="text-gray-400 hover:text-gray-600"
                                >
                                    <X size={24} />
                                </button>
                            </div>

                            <div className="mb-6">
                                <p className="text-sm text-gray-600 mb-2">Pedido: {currentPedido.codigo}</p>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Nuevo Estado
                                </label>
                                <select
                                    value={newStatus}
                                    onChange={(e) => setNewStatus(e.target.value)}
                                    className="w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-[#2e7e8b] focus:border-[#2e7e8b]"
                                >
                                    <option value="pendiente">Pendiente</option>
                                    <option value="pagado">Pagado</option>
                                    <option value="enviado">Enviado</option>
                                    <option value="entregado">Entregado</option>
                                    <option value="cancelado">Cancelado</option>
                                </select>
                            </div>

                            <div className="flex gap-3">
                                <button
                                    onClick={guardarEstado}
                                    className="flex-1 inline-flex items-center justify-center gap-2 rounded-md bg-[#2e7e8b] px-4 py-2 text-white font-semibold hover:bg-[#256a76] transition"
                                >
                                    <CheckCircle size={16} />
                                    Guardar
                                </button>
                                <button
                                    onClick={() => setShowStatusModal(false)}
                                    className="flex-1 inline-flex items-center justify-center gap-2 rounded-md border border-gray-300 px-4 py-2 text-gray-700 font-semibold hover:bg-gray-50 transition"
                                >
                                    Cancelar
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
