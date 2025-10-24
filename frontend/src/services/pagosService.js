// src/services/pagosService.js
import api from './api';

const pagosService = {
    iniciarPago: async (pedidoId) => {
        try {
            const response = await api.post(`/ecommerce/pedidos/${pedidoId}/iniciar-pago/`);
            return response.data;
        } catch (error) {
            console.error('Error al iniciar pago:', error);
            throw error;
        }
    },

    confirmarPago: async (pedidoId) => {
        try {
            const response = await api.post(`/ecommerce/pedidos/${pedidoId}/marcar_pagado/`);
            return response.data;
        } catch (error) {
            console.error('Error al confirmar pago:', error);
            throw error;
        }
    },
};

export default pagosService;
