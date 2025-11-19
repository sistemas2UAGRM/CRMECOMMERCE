// frontend/src/modulos/carrito/GestionCarritos.jsx
import React, { useEffect, useState } from "react";
import {
    ShoppingCart, Package2, Eye, Search as SearchIcon,
    Filter, RefreshCw, User, Calendar, DollarSign,
    AlertCircle, CheckCircle, Clock, X
} from "lucide-react";
import api from '../../services/api';
import { toast } from 'react-hot-toast';

const ESTADO_CARRITO = {
    'activo': { name: 'Activo', color: 'bg-green-100 text-green-800' },
    'pendiente': { name: 'Pendiente', color: 'bg-yellow-100 text-yellow-800' },
    'completado': { name: 'Completado', color: 'bg-blue-100 text-blue-800' },
    'cancelado': { name: 'Cancelado', color: 'bg-red-100 text-red-800' },
};

export default function GestionCarritos() {
    const [carritos, setCarritos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [pageInfo, setPageInfo] = useState({ next: null, previous: null, count: 0 });
    const [page, setPage] = useState(1);
    const [query, setQuery] = useState("");
    const [estadoFilter, setEstadoFilter] = useState(""); // filtro por estado

    const [showDetailsModal, setShowDetailsModal] = useState(false);
    const [currentCarrito, setCurrentCarrito] = useState(null);

    // Función para obtener carritos de la API
    const fetchCarritos = async (currentPage = 1, searchQuery = "", estadoFilterParam = estadoFilter) => {
        setLoading(true);
        setError(null);
        try {
            const params = {
                page: currentPage,
                search: searchQuery
            };

            if (estadoFilterParam) {
                params.estado = estadoFilterParam;
            }

            const { data } = await api.get("/ecommerce/carritos/", { params });

            setCarritos(data.results || []);
            setPageInfo({
                next: data.next,
                previous: data.previous,
                count: data.count || 0,
                num_pages: data.num_pages || 1
            });
            setPage(currentPage);
        } catch (err) {
            console.error("Error al cargar carritos:", err);
            if (err.response?.status === 403) {
                setError("No tienes permisos para ver los carritos.");
            } else {
                setError("Error al cargar carritos.");
            }
        } finally {
            setLoading(false);
        }
    };

    // Cargar carritos al montar el componente
    useEffect(() => {
        fetchCarritos(1, "");
    }, []);

    // Efecto para aplicar filtros automáticamente
    useEffect(() => {
        const timeoutId = setTimeout(() => {
            setPage(1);
            fetchCarritos(1, query, estadoFilter);
        }, 300);

        return () => clearTimeout(timeoutId);
    }, [estadoFilter]);

    // Handler para búsqueda
    const handleSearchSubmit = (e) => {
        if (e) e.preventDefault();
        setPage(1);
        fetchCarritos(1, query, estadoFilter);
    };

    // Función para ver detalles del carrito
    const verDetalles = async (carrito) => {
        try {
            const { data } = await api.get(`/ecommerce/carritos/${carrito.id}/`);
            setCurrentCarrito(data);
            setShowDetailsModal(true);
        } catch (err) {
            console.error("Error al cargar detalles:", err);
            toast.error("Error al cargar detalles del carrito");
        }
    };

    // Función para formatear fecha
    const formatearFecha = (fechaString) => {
        if (!fechaString) return "No especificado";
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
                                <ShoppingCart size={24} className="text-white" />
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold text-gray-900">Gestión de Carritos</h1>
                                <p className="text-gray-600">Administra todos los carritos del sistema</p>
                            </div>
                        </div>

                        <button
                            onClick={() => fetchCarritos(1, query, estadoFilter)}
                            disabled={loading}
                            className="inline-flex items-center gap-2 rounded-md bg-gray-100 px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-200 transition disabled:opacity-50"
                        >
                            <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
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
                                    placeholder="Usuario, ID del carrito..."
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
                                <option value="activo">Activo</option>
                                <option value="pendiente">Pendiente</option>
                                <option value="completado">Completado</option>
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
                            <span className="ml-3 text-gray-600">Cargando carritos...</span>
                        </div>
                    </div>
                )}

                {/* Error */}
                {error && (
                    <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
                        <div className="flex items-center gap-3 text-red-600">
                            <AlertCircle size={24} />
                            <div>
                                <h3 className="font-semibold">Error</h3>
                                <p className="text-sm">{error}</p>
                            </div>
                        </div>
                    </div>
                )}

                {/* Lista de carritos */}
                {!loading && !error && (
                    <>
                        {/* Estadísticas */}
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                            <div className="bg-white p-4 rounded-lg shadow-sm">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm text-gray-600">Total Carritos</p>
                                        <p className="text-2xl font-bold text-gray-900">{pageInfo.count}</p>
                                    </div>
                                    <ShoppingCart className="h-8 w-8 text-blue-600" />
                                </div>
                            </div>
                            <div className="bg-white p-4 rounded-lg shadow-sm">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm text-gray-600">Carritos Activos</p>
                                        <p className="text-2xl font-bold text-green-600">
                                            {carritos.filter(c => c.estado === 'activo').length}
                                        </p>
                                    </div>
                                    <CheckCircle className="h-8 w-8 text-green-600" />
                                </div>
                            </div>
                        </div>

                        {/* Tabla de carritos */}
                        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
                            <div className="overflow-x-auto">
                                <table className="w-full">
                                    <thead className="bg-gray-50 border-b border-gray-200">
                                        <tr>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Carrito
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Usuario
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Estado
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Productos
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Total
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Fecha
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Acciones
                                            </th>
                                        </tr>
                                    </thead>
                                    <tbody className="bg-white divide-y divide-gray-200">
                                        {carritos.length === 0 ? (
                                            <tr>
                                                <td colSpan="7" className="px-6 py-12 text-center">
                                                    <Package2 size={48} className="mx-auto text-gray-400 mb-4" />
                                                    <h3 className="text-lg font-medium text-gray-900 mb-2">No hay carritos</h3>
                                                    <p className="text-gray-600">No se encontraron carritos que coincidan con los filtros.</p>
                                                </td>
                                            </tr>
                                        ) : (
                                            carritos.map((carrito) => (
                                                <tr key={carrito.id} className="hover:bg-gray-50">
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <div className="flex items-center">
                                                            <div className="p-2 bg-gray-100 rounded-lg mr-3">
                                                                <ShoppingCart size={16} className="text-gray-600" />
                                                            </div>
                                                            <div>
                                                                <div className="text-sm font-medium text-gray-900">#{carrito.id}</div>
                                                                <div className="text-sm text-gray-500">ID: {carrito.id}</div>
                                                            </div>
                                                        </div>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <div className="flex items-center">
                                                            <User size={16} className="text-gray-400 mr-2" />
                                                            <div>
                                                                <div className="text-sm font-medium text-gray-900">
                                                                    {carrito.usuario?.first_name} {carrito.usuario?.last_name}
                                                                </div>
                                                                <div className="text-sm text-gray-500">@{carrito.usuario?.username}</div>
                                                            </div>
                                                        </div>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${ESTADO_CARRITO[carrito.estado]?.color || 'bg-gray-100 text-gray-800'}`}>
                                                            {ESTADO_CARRITO[carrito.estado]?.name || carrito.estado}
                                                        </span>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                        {carrito.total_productos || 0} productos
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <div className="text-sm font-medium text-gray-900">
                                                            {formatearPrecio(carrito.total || 0)}
                                                        </div>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                        <div className="flex items-center">
                                                            <Calendar size={14} className="mr-1" />
                                                            {formatearFecha(carrito.fecha_creacion)}
                                                        </div>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                                        <button
                                                            onClick={() => verDetalles(carrito)}
                                                            className="inline-flex items-center gap-1 text-[#2e7e8b] hover:text-[#256a76] transition"
                                                        >
                                                            <Eye size={16} />
                                                            Ver detalles
                                                        </button>
                                                    </td>
                                                </tr>
                                            ))
                                        )}
                                    </tbody>
                                </table>
                            </div>

                            {/* Paginación */}
                            {pageInfo.num_pages > 1 && (
                                <div className="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
                                    <div className="flex items-center justify-between">
                                        <div className="text-sm text-gray-700">
                                            Página <span className="font-medium">{page}</span> de{" "}
                                            <span className="font-medium">{pageInfo.num_pages}</span> - Total:{" "}
                                            <span className="font-medium">{pageInfo.count}</span> carritos
                                        </div>
                                        <div className="flex gap-2">
                                            <button
                                                onClick={() => fetchCarritos(page - 1, query, estadoFilter)}
                                                disabled={!pageInfo.previous}
                                                className="px-3 py-1 text-sm bg-gray-100 rounded hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
                                            >
                                                Anterior
                                            </button>
                                            <button
                                                onClick={() => fetchCarritos(page + 1, query, estadoFilter)}
                                                disabled={!pageInfo.next}
                                                className="px-3 py-1 text-sm bg-gray-100 rounded hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
                                            >
                                                Siguiente
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </>
                )}

                {/* Modal de detalles */}
                {showDetailsModal && currentCarrito && (
                    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                        <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                            <div className="p-6 border-b border-gray-200">
                                <div className="flex items-center justify-between">
                                    <h2 className="text-xl font-semibold text-gray-900">
                                        Detalles del Carrito #{currentCarrito.id}
                                    </h2>
                                    <button
                                        onClick={() => setShowDetailsModal(false)}
                                        className="p-2 hover:bg-gray-100 rounded-lg transition"
                                    >
                                        <X size={20} />
                                    </button>
                                </div>
                            </div>

                            <div className="p-6">
                                {/* Información del usuario */}
                                <div className="mb-6">
                                    <h3 className="text-lg font-medium text-gray-900 mb-3">Información del Usuario</h3>
                                    <div className="bg-gray-50 rounded-lg p-4">
                                        <p><strong>Nombre:</strong> {currentCarrito.usuario?.first_name} {currentCarrito.usuario?.last_name}</p>
                                        <p><strong>Usuario:</strong> @{currentCarrito.usuario?.username}</p>
                                        <p><strong>Email:</strong> {currentCarrito.usuario?.email}</p>
                                    </div>
                                </div>

                                {/* Productos del carrito */}
                                <div className="mb-6">
                                    <h3 className="text-lg font-medium text-gray-900 mb-3">Productos</h3>
                                    <div className="space-y-3">
                                        {currentCarrito.productos?.map((item, index) => (
                                            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                                <div className="flex items-center gap-3">
                                                    <div className="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center">
                                                        <Package2 size={20} className="text-gray-400" />
                                                    </div>
                                                    <div>
                                                        <p className="font-medium text-gray-900">{item.producto_nombre}</p>
                                                        <p className="text-sm text-gray-600">Cantidad: {item.cantidad}</p>
                                                    </div>
                                                </div>
                                                <div className="text-right">
                                                    <p className="font-medium text-gray-900">{formatearPrecio(item.subtotal)}</p>
                                                    <p className="text-sm text-gray-600">{formatearPrecio(item.precio_unitario)} c/u</p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Resumen */}
                                <div className="bg-gray-50 rounded-lg p-4">
                                    <div className="flex justify-between items-center mb-2">
                                        <span>Subtotal:</span>
                                        <span>{formatearPrecio(currentCarrito.subtotal || 0)}</span>
                                    </div>
                                    {currentCarrito.descuento > 0 && (
                                        <div className="flex justify-between items-center mb-2 text-green-600">
                                            <span>Descuento:</span>
                                            <span>-{formatearPrecio(currentCarrito.descuento)}</span>
                                        </div>
                                    )}
                                    <div className="flex justify-between items-center font-semibold text-lg border-t pt-2">
                                        <span>Total:</span>
                                        <span>{formatearPrecio(currentCarrito.total || 0)}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}