import api from './api';

const aiService = {
  // Función para predicciones de ventas
  predictSales: async (dias) => {
    try {
      const response = await api.post('/predictions/predecir/', { 
        dias_a_predecir: dias  // Cambio de 'dias' a 'dias_a_predecir' para coincidir con el schema del microservicio
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Función para generar reportes con IA
  generateReport: async (prompt, formato = 'json') => {
    try {
      // El microservicio determina el formato desde el prompt usando IA
      // pero mantenemos el parámetro para futuras extensiones
      const response = await api.post('/reports/generar-reporte-ia/', { 
        prompt,
        formato 
      }, {
        responseType: formato !== 'json' ? 'blob' : 'json'  // Configurar para recibir archivos binarios
      });
      return response;
    } catch (error) {
      throw error;
    }
  },
};

export default aiService;