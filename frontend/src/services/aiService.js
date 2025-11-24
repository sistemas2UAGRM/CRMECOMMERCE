import api from './api';
import { getAuthToken } from '../utils/auth';

const aiService = {
  // Función para predicciones de ventas
  // El backend Django (API Gateway) redirige a http://localhost:8002
  predictSales: async (dias) => {
    try {
      const response = await api.post('/ai/predictions/predecir/', {
        dias_a_predecir: dias
      });
      return response.data;
    } catch (error) {
      console.error('Error en predictSales:', error);
      throw error;
    }
  },

  // Función para generar reportes con IA
  // El backend Django (API Gateway) redirige a http://localhost:8001
  generateReport: async (prompt, formato = 'json') => {
    try {
      const response = await api.post('/ai/reports/generar-reporte-ia/', {
        prompt,
        formato
      }, {
        responseType: formato !== 'json' ? 'blob' : 'json'
      });
      return response;
    } catch (error) {
      console.error('Error en generateReport:', error);
      throw error;
    }
  },
};

export default aiService;