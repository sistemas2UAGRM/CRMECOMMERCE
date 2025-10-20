// src/services/carritosService.js (NUEVO)
import api from './api';

const ENDPOINT_BASE = '/ecommerce/carrito';

// GET /api/ecommerce/carrito/
const obtenerMiCarrito = async () => {
    const response = await api.get(`${ENDPOINT_BASE}/`);
    return response.data;
};

// POST /api/ecommerce/carrito/agregar_item/
const agregarItem = async (productoId, cantidad) => {
    const payload = { producto_id: productoId, cantidad };
    const response = await api.post(`${ENDPOINT_BASE}/agregar_item/`, payload);
    return response.data;
};

// DELETE /api/ecommerce/carrito/items/{pk}/eliminar/
const eliminarItem = async (itemId) => {
    await api.delete(`${ENDPOINT_BASE}/items/${itemId}/eliminar/`);
};

// POST /api/ecommerce/carrito/crear_pedido/
const crearPedidoDesdeCarrito = async (direccionEnvio) => {
    const payload = { direccion_envio: direccionEnvio };
    const response = await api.post(`${ENDPOINT_BASE}/crear_pedido/`, payload);
    return response.data;
};

export default {
    obtenerMiCarrito,
    agregarItem,
    eliminarItem,
    crearPedidoDesdeCarrito,
};