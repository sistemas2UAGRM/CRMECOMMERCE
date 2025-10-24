import React, { useEffect, useState } from 'react';
import pedidosService from '../../../../services/pedidosService';

export default function Pedidos() {
    const [pedidos, setPedidos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchPedidos = async () => {
            try {
                setLoading(true);
                const data = await pedidosService.listarPedidosUsuario();
                setPedidos(data);
                setError(null);
            } catch (err) {
                console.error('Error al obtener pedidos:', err);
                setError('No se pudieron cargar los pedidos.');
            } finally {
                setLoading(false);
            }
        };

        fetchPedidos();
    }, []);

    if (loading) return <div className="text-center py-12 text-gray-500">Cargando pedidos...</div>;
    if (error) return <div className="text-center py-12 text-red-600 bg-red-50 p-4 rounded-md">{error}</div>;

    return (
        <div className="p-6">
            <h1 className="text-3xl font-bold tracking-tight text-gray-900 mb-8">Mis Pedidos</h1>
            {pedidos.length > 0 ? (
                <div className="space-y-4">
                    {pedidos.map((pedido) => (
                        <div key={pedido.id} className="border p-4 rounded-md shadow-sm">
                            <h3 className="text-lg font-semibold text-gray-800">Pedido #{pedido.id}</h3>
                            <p className="text-sm text-gray-500">Fecha: {new Date(pedido.fecha_creacion).toLocaleDateString()}</p>
                            <p className="text-sm text-gray-500">Estado: {pedido.estado}</p>
                            <p className="text-sm text-gray-500">Total: ${pedido.total.toFixed(2)}</p>
                        </div>
                    ))}
                </div>
            ) : (
                <p className="text-center text-gray-500">No tienes pedidos registrados.</p>
            )}
        </div>
    );
}