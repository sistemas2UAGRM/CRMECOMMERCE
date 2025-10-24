import api from './api';

const pedidosService = {
    listar: async () => {
        try {
            const response = await api.get('/ecommerce/pedidos/'); // Ajusta la ruta según tu backend
            return response.data;
        } catch (error) {
            console.error('Error al listar pedidos:', error);
            throw error;
        }
    },

    obtener: async (id) => {
        try {
            const response = await api.get(`/ecommerce/pedidos/${id}/`);
            return response.data;
        } catch (error) {
            console.error(`Error al obtener el pedido con ID ${id}:`, error);
            throw error;
        }
    },

    crear: async (pedido) => {
        try {
            const response = await api.post('/ecommerce/pedidos/', pedido);
            return response.data;
        } catch (error) {
            console.error('Error al crear un pedido:', error);
            throw error;
        }
    },

    actualizar: async (id, pedido) => {
        try {
            const response = await api.put(`/ecommerce/pedidos/${id}/`, pedido);
            return response.data;
        } catch (error) {
            console.error(`Error al actualizar el pedido con ID ${id}:`, error);
            throw error;
        }
    },

    eliminar: async (id) => {
        try {
            const response = await api.delete(`/ecommerce/pedidos/${id}/`);
            return response.data;
        } catch (error) {
            console.error(`Error al eliminar el pedido con ID ${id}:`, error);
            throw error;
        }
    },

    listarPedidosUsuario: async () => {
        try {
            console.log('=== Llamando a listarPedidosUsuario ===');
            console.log('URL:', '/ecommerce/pedidos/');
            const response = await api.get('/ecommerce/pedidos/');
            console.log('Respuesta status:', response.status);
            console.log('Respuesta headers:', response.headers);
            console.log('Respuesta data:', response.data);
            return response.data;
        } catch (error) {
            console.error('Error al listar pedidos del usuario:', error);
            console.error('Error response:', error.response?.data);
            console.error('Error status:', error.response?.status);
            throw error;
        }
    },
};

export default pedidosService;