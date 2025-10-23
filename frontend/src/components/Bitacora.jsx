import { useState, useEffect } from 'react';
import { Clock, User, FileText, Globe, Search, Download, Filter, ChevronLeft, ChevronRight } from 'lucide-react';
import api from '../services/api';

const Bitacora = () => {
    // Estados principales
    const [logs, setLogs] = useState([]);
    const [filteredLogs, setFilteredLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    // Estados de filtros
    const [filters, setFilters] = useState({
        fechaInicio: '',
        fechaFin: '',
        usuario: '',
        accion: '',
        ip: ''
    });

    // Estados de búsqueda
    const [searchTerm, setSearchTerm] = useState('');
    const [showFilters, setShowFilters] = useState(false);

    // Estados de paginación
    const [currentPage, setCurrentPage] = useState(1);
    const [itemsPerPage] = useState(10);
    const [totalItems, setTotalItems] = useState(0);

    // Función para obtener datos de bitácora
    const fetchLogs = async (page = 1) => {
        try {
            setLoading(true);

            const params = {
                page,
            };
            if (filters.fechaInicio) params.fecha_inicio = filters.fechaInicio;
            if (filters.fechaFin) params.fecha_fin = filters.fechaFin;
            if (filters.usuario) params.usuario_id = filters.usuario;
            if (filters.accion) params.accion_contiene = filters.accion;
            if (filters.ip) params.ip = filters.ip;

            const response = await api.get('/common/bitacora/', { params });

            const data = response.data;
            setLogs(data.results || []);
            setFilteredLogs(data.results || []);
            setTotalItems(data.count || 0);
            setError('');
        } catch (err) {
            console.error("Error fetching logs:", err);
            const msg =
                err.response?.data?.detail ||
                err.response?.data?.message ||
                JSON.stringify(err.response?.data) ||
                "Error al cargar los datos";
            setError(msg);
        } finally {
            setLoading(false);
        }
    };

    // Cargar datos al montar el componente
    useEffect(() => {
        fetchLogs(currentPage);
    }, [currentPage, filters]);

    // Función de búsqueda local
    const handleSearch = (term) => {
        setSearchTerm(term);
        if (!term.trim()) {
            setFilteredLogs(logs);
            return;
        }

        const filtered = logs.filter(log =>
            log.accion.toLowerCase().includes(term.toLowerCase()) ||
            log.usuario?.username?.toLowerCase().includes(term.toLowerCase()) ||
            log.ip.includes(term)
        );
        setFilteredLogs(filtered);
    };

    // Función para aplicar filtros
    const applyFilters = () => {
        setCurrentPage(1); // Reset to first page when applying filters
        fetchLogs(1);
    };

    // Función para limpiar filtros
    const clearFilters = () => {
        setFilters({
            fechaInicio: '',
            fechaFin: '',
            usuario: '',
            accion: '',
            ip: ''
        });
        setSearchTerm('');
        setCurrentPage(1);
    };

    // Función para exportar datos
    const exportData = async (format = 'json') => {
        try {
            const response = await api.get(`/common/export/`, {
                params: { format },
                responseType: 'blob',
            });

            const blob = response.data;
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `bitacora_${new Date().toISOString().split('T')[0]}.${format}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (err) {
            console.error('Error exporting data:', err);
            const msg =
                err.response?.data?.detail ||
                err.response?.data?.message ||
                'Error al exportar datos';
            alert(msg);
        }
    };

    // Formatear fecha
    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleString('es-ES', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    // Cálculo de paginación
    const totalPages = Math.ceil(totalItems / itemsPerPage);

    return (
        <div className="p-6 bg-gray-50 min-h-screen">
            {/* Header */}
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-800 mb-2">Bitácora de Auditoría</h1>
                <p className="text-gray-600">Registro completo de actividades del sistema</p>
            </div>

            {/* Controles superiores */}
            <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
                <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
                    {/* Barra de búsqueda */}
                    <div className="flex-1 max-w-md">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                            <input
                                type="text"
                                placeholder="Buscar en acciones, usuarios o IP..."
                                value={searchTerm}
                                onChange={(e) => handleSearch(e.target.value)}
                                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                        </div>
                    </div>

                    {/* Botones de acción */}
                    <div className="flex gap-2">
                        <button
                            onClick={() => setShowFilters(!showFilters)}
                            className="flex items-center gap-2 px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                        >
                            <Filter className="w-4 h-4" />
                            Filtros
                        </button>

                        <div className="relative group">
                            <button className="flex items-center gap-2 px-4 py-2 text-white bg-green-600 rounded-lg hover:bg-green-700 transition-colors">
                                <Download className="w-4 h-4" />
                                Exportar
                            </button>
                            <div className="absolute right-0 top-full mt-2 bg-white border border-gray-200 rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-10">
                                <button
                                    onClick={() => exportData('json')}
                                    className="block w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-50 first:rounded-t-lg"
                                >
                                    JSON
                                </button>
                                <button
                                    onClick={() => exportData('csv')}
                                    className="block w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-50"
                                >
                                    CSV
                                </button>
                                <button
                                    onClick={() => exportData('txt')}
                                    className="block w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-50 last:rounded-b-lg"
                                >
                                    TXT
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Panel de filtros */}
                {showFilters && (
                    <div className="mt-4 p-4 border-t border-gray-200">
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Fecha Inicio</label>
                                <input
                                    type="date"
                                    value={filters.fechaInicio}
                                    onChange={(e) => setFilters({ ...filters, fechaInicio: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Fecha Fin</label>
                                <input
                                    type="date"
                                    value={filters.fechaFin}
                                    onChange={(e) => setFilters({ ...filters, fechaFin: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Usuario ID</label>
                                <input
                                    type="number"
                                    placeholder="ID del usuario"
                                    value={filters.usuario}
                                    onChange={(e) => setFilters({ ...filters, usuario: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Acción</label>
                                <input
                                    type="text"
                                    placeholder="Contiene texto..."
                                    value={filters.accion}
                                    onChange={(e) => setFilters({ ...filters, accion: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">IP</label>
                                <input
                                    type="text"
                                    placeholder="Dirección IP"
                                    value={filters.ip}
                                    onChange={(e) => setFilters({ ...filters, ip: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                />
                            </div>
                        </div>
                        <div className="mt-4 flex gap-2">
                            <button
                                onClick={applyFilters}
                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                            >
                                Aplicar Filtros
                            </button>
                            <button
                                onClick={clearFilters}
                                className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
                            >
                                Limpiar
                            </button>
                        </div>
                    </div>
                )}
            </div>

            {/* Estado de carga */}
            {loading && (
                <div className="bg-white rounded-lg shadow-sm p-8 text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Cargando datos de bitácora...</p>
                </div>
            )}

            {/* Error */}
            {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                    <p className="text-red-800">{error}</p>
                </div>
            )}

            {/* Tabla de bitácora */}
            {!loading && !error && (
                <div className="bg-white rounded-lg shadow-sm overflow-hidden">
                    {filteredLogs.length === 0 ? (
                        <div className="p-8 text-center text-gray-500">
                            <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                            <p>No se encontraron registros de auditoría</p>
                        </div>
                    ) : (
                        <>
                            <div className="overflow-x-auto">
                                <table className="w-full">
                                    <thead className="bg-gray-50 border-b border-gray-200">
                                        <tr>
                                            <th className="text-left p-4 font-medium text-gray-900">Fecha</th>
                                            <th className="text-left p-4 font-medium text-gray-900">Usuario</th>
                                            <th className="text-left p-4 font-medium text-gray-900">Acción</th>
                                            <th className="text-left p-4 font-medium text-gray-900">IP</th>
                                            <th className="text-left p-4 font-medium text-gray-900">Tiempo</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-200">
                                        {filteredLogs.map((log) => (
                                            <tr key={log.id} className="hover:bg-gray-50 transition-colors">
                                                <td className="p-4">
                                                    <div className="flex items-center gap-2 text-sm">
                                                        <Clock className="w-4 h-4 text-gray-400" />
                                                        {formatDate(log.fecha)}
                                                    </div>
                                                </td>
                                                <td className="p-4">
                                                    <div className="flex items-center gap-2">
                                                        <User className="w-4 h-4 text-gray-400" />
                                                        <div>
                                                            <div className="font-medium text-gray-900">
                                                                {log.usuario?.username || 'Sistema'}
                                                            </div>
                                                            {log.usuario?.email && (
                                                                <div className="text-xs text-gray-500">
                                                                    {log.usuario.email}
                                                                </div>
                                                            )}
                                                        </div>
                                                    </div>
                                                </td>
                                                <td className="p-4">
                                                    <div className="flex items-center gap-2">
                                                        <FileText className="w-4 h-4 text-gray-400" />
                                                        <span className="text-sm text-gray-900">{log.accion}</span>
                                                    </div>
                                                </td>
                                                <td className="p-4">
                                                    <div className="flex items-center gap-2">
                                                        <Globe className="w-4 h-4 text-gray-400" />
                                                        <span className="text-sm text-gray-600 font-mono">{log.ip}</span>
                                                    </div>
                                                </td>
                                                <td className="p-4">
                                                    <span className="text-xs text-gray-500">
                                                        {log.tiempo_transcurrido || 'Reciente'}
                                                    </span>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>

                            {/* Paginación */}
                            {totalPages > 1 && (
                                <div className="border-t border-gray-200 px-4 py-3 flex items-center justify-between">
                                    <div className="text-sm text-gray-700">
                                        Mostrando {((currentPage - 1) * itemsPerPage) + 1} a {Math.min(currentPage * itemsPerPage, totalItems)} de {totalItems} registros
                                    </div>
                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                                            disabled={currentPage === 1}
                                            className="flex items-center gap-1 px-3 py-1 text-sm text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                                        >
                                            <ChevronLeft className="w-4 h-4" />
                                            Anterior
                                        </button>
                                        <span className="flex items-center px-3 py-1 text-sm text-gray-700">
                                            Página {currentPage} de {totalPages}
                                        </span>
                                        <button
                                            onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                                            disabled={currentPage === totalPages}
                                            className="flex items-center gap-1 px-3 py-1 text-sm text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                                        >
                                            Siguiente
                                            <ChevronRight className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                            )}
                        </>
                    )}
                </div>
            )}
        </div>
    );
};

export default Bitacora;