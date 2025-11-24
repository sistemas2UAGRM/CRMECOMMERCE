import React, { useState } from 'react';
import toast from 'react-hot-toast';
import aiService from '../../services/aiService';
import { Bot, TrendingUp, Calendar, Loader, Download, BarChart3, LineChart, ArrowUp, ArrowDown } from 'lucide-react';
import { LineChart as RechartsLine, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts';

export default function PredictionPage() {
  const [dias, setDias] = useState('');
  const [predicciones, setPredicciones] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [vistaActual, setVistaActual] = useState('chart'); // 'chart' o 'table'

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!dias || dias <= 0) {
      toast.error('Por favor ingresa un número válido de días.');
      return;
    }

    setCargando(true);
    try {
      const data = await aiService.predictSales(parseInt(dias));
      setPredicciones(data);
      toast.success('Predicciones generadas exitosamente.');
    } catch (error) {
      toast.error('Error al generar predicciones. Intenta nuevamente.');
      console.error(error);
    } finally {
      setCargando(false);
    }
  };

  const exportarCSV = () => {
    if (!predicciones || !predicciones.predicciones) return;
    
    const csvContent = [
      ['Fecha', 'Predicción de Ventas'],
      ...predicciones.predicciones.map(p => [p.fecha, p.prediccion_venta || p.prediccion])
    ].map(row => row.join(',')).join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `predicciones_ventas_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    toast.success('CSV exportado exitosamente');
  };

  const calcularEstadisticas = () => {
    if (!predicciones || !predicciones.predicciones) return null;
    
    const valores = predicciones.predicciones.map(p => parseFloat(p.prediccion_venta || p.prediccion));
    const total = valores.reduce((sum, val) => sum + val, 0);
    const promedio = total / valores.length;
    const maximo = Math.max(...valores);
    const minimo = Math.min(...valores);
    
    // Calcular tendencia (comparando primera y última semana)
    const primeraSemana = valores.slice(0, 7).reduce((sum, val) => sum + val, 0) / 7;
    const ultimaSemana = valores.slice(-7).reduce((sum, val) => sum + val, 0) / 7;
    const tendencia = ((ultimaSemana - primeraSemana) / primeraSemana) * 100;
    
    return { total, promedio, maximo, minimo, tendencia };
  };

  const estadisticas = calcularEstadisticas();

  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      <div className="flex items-center mb-6">
        <Bot className="mr-3 text-blue-600" size={32} />
        <h1 className="text-2xl font-bold text-gray-800">Predicciones de Ventas con IA</h1>
      </div>

      <form onSubmit={handleSubmit} className="mb-6">
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <label htmlFor="dias" className="block text-sm font-medium text-gray-700 mb-2">
              Número de días a predecir
            </label>
            <input
              type="number"
              id="dias"
              value={dias}
              onChange={(e) => setDias(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Ej: 30"
              min="1"
              required
            />
          </div>
          <div className="flex items-end">
            <button
              type="submit"
              disabled={cargando}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 flex items-center"
            >
              {cargando ? <Loader className="animate-spin mr-2" size={16} /> : <TrendingUp className="mr-2" size={16} />}
              {cargando ? 'Generando...' : 'Predecir'}
            </button>
          </div>
        </div>
      </form>

      {predicciones && estadisticas && (
        <div className="mt-6 space-y-6">
          {/* Tarjetas de Estadísticas */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-4 text-white shadow-lg">
              <div className="text-sm opacity-90 mb-1">Total Proyectado</div>
              <div className="text-2xl font-bold">${estadisticas.total.toFixed(2)}</div>
            </div>
            <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-4 text-white shadow-lg">
              <div className="text-sm opacity-90 mb-1">Promedio Diario</div>
              <div className="text-2xl font-bold">${estadisticas.promedio.toFixed(2)}</div>
            </div>
            <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg p-4 text-white shadow-lg">
              <div className="text-sm opacity-90 mb-1">Máximo</div>
              <div className="text-2xl font-bold">${estadisticas.maximo.toFixed(2)}</div>
            </div>
            <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg p-4 text-white shadow-lg">
              <div className="text-sm opacity-90 mb-1">Mínimo</div>
              <div className="text-2xl font-bold">${estadisticas.minimo.toFixed(2)}</div>
            </div>
            <div className={`bg-gradient-to-br ${estadisticas.tendencia >= 0 ? 'from-teal-500 to-teal-600' : 'from-red-500 to-red-600'} rounded-lg p-4 text-white shadow-lg`}>
              <div className="text-sm opacity-90 mb-1">Tendencia</div>
              <div className="flex items-center text-2xl font-bold">
                {estadisticas.tendencia >= 0 ? <ArrowUp size={24} /> : <ArrowDown size={24} />}
                {Math.abs(estadisticas.tendencia).toFixed(1)}%
              </div>
            </div>
          </div>

          {/* Controles de Vista */}
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-800 flex items-center">
              <Calendar className="mr-2" size={20} />
              Resultados de Predicción ({predicciones.dias_solicitados} días)
            </h2>
            <div className="flex space-x-2">
              <button
                onClick={() => setVistaActual('chart')}
                className={`px-4 py-2 rounded-md flex items-center transition-colors ${
                  vistaActual === 'chart' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                <LineChart className="mr-2" size={16} />
                Gráfico
              </button>
              <button
                onClick={() => setVistaActual('table')}
                className={`px-4 py-2 rounded-md flex items-center transition-colors ${
                  vistaActual === 'table' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                <BarChart3 className="mr-2" size={16} />
                Tabla
              </button>
              <button
                onClick={exportarCSV}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 flex items-center transition-colors"
              >
                <Download className="mr-2" size={16} />
                Exportar CSV
              </button>
            </div>
          </div>

          {/* Vista de Gráfico */}
          {vistaActual === 'chart' && (
            <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
              <ResponsiveContainer width="100%" height={400}>
                <AreaChart data={predicciones.predicciones}>
                  <defs>
                    <linearGradient id="colorPrediccion" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.1}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                  <XAxis 
                    dataKey="fecha" 
                    stroke="#6B7280"
                    tick={{ fontSize: 12 }}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis 
                    stroke="#6B7280"
                    tick={{ fontSize: 12 }}
                    tickFormatter={(value) => `$${value.toFixed(0)}`}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1F2937', 
                      border: 'none', 
                      borderRadius: '8px',
                      color: '#fff'
                    }}
                    formatter={(value) => [`$${parseFloat(value).toFixed(2)}`, 'Predicción']}
                  />
                  <Legend />
                  <Area 
                    type="monotone" 
                    dataKey={(item) => item.prediccion_venta || item.prediccion}
                    stroke="#3B82F6" 
                    strokeWidth={3}
                    fill="url(#colorPrediccion)"
                    name="Predicción de Ventas"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Vista de Tabla */}
          {vistaActual === 'table' && (
            <div className="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-200">
              <table className="min-w-full">
                <thead>
                  <tr className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
                    <th className="px-6 py-3 text-left text-sm font-semibold">Fecha</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold">Predicción de Ventas</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold">Desviación del Promedio</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {predicciones.predicciones && predicciones.predicciones.map((pred, index) => {
                    const valor = parseFloat(pred.prediccion_venta || pred.prediccion);
                    const desviacion = ((valor - estadisticas.promedio) / estadisticas.promedio) * 100;
                    return (
                      <tr key={index} className="hover:bg-blue-50 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">
                          {pred.fecha}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-semibold">
                          ${valor.toFixed(2)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            desviacion >= 0 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {desviacion >= 0 ? '+' : ''}{desviacion.toFixed(1)}%
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}