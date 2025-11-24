import React, { useState } from 'react';
import toast from 'react-hot-toast';
import aiService from '../../services/aiService';
import { FileText, Download, Loader, File, Sparkles, X, Eye, History, Copy, Mic, MicOff } from 'lucide-react';

const PLANTILLAS_PROMPT = [
  {
    titulo: 'Ventas Mensuales',
    descripcion: 'Reporte de ventas del mes actual',
    prompt: 'Genera un reporte de todas las ventas del mes actual con totales por producto'
  },
  {
    titulo: 'Clientes Activos',
    descripcion: 'Lista de clientes con actividad reciente',
    prompt: 'Muestra un reporte de los clientes que han realizado compras en los últimos 30 días'
  },
  {
    titulo: 'Productos Más Vendidos',
    descripcion: 'Top 10 productos más vendidos',
    prompt: 'Genera un reporte de los 10 productos más vendidos con cantidades y totales'
  },
  {
    titulo: 'Análisis de Inventario',
    descripcion: 'Estado actual del inventario',
    prompt: 'Crea un reporte del inventario actual mostrando productos con stock bajo'
  },
  {
    titulo: 'Reporte Financiero',
    descripcion: 'Resumen financiero del trimestre',
    prompt: 'Genera un reporte financiero del trimestre actual con ingresos, gastos y utilidades'
  }
];

export default function ReportPage() {
  const [prompt, setPrompt] = useState('');
  const [formato, setFormato] = useState('json');
  const [reporte, setReporte] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [mostrarPlantillas, setMostrarPlantillas] = useState(false);
  const [mostrarVistaPrevia, setMostrarVistaPrevia] = useState(false);
  const [historialReportes, setHistorialReportes] = useState([]);
  const [isListening, setIsListening] = useState(false);

  const handleVoiceInput = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      toast.error('Tu navegador no soporta reconocimiento de voz. Intenta con Chrome o Edge.');
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.lang = 'es-ES';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
      setIsListening(true);
      toast.success('Escuchando... habla ahora');
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setPrompt((prev) => (prev ? `${prev} ${transcript}` : transcript));
      setIsListening(false);
    };

    recognition.onerror = (event) => {
      console.error('Error de reconocimiento de voz:', event.error);
      setIsListening(false);
      if (event.error === 'not-allowed') {
        toast.error('Permiso de micrófono denegado.');
      } else {
        toast.error('No se pudo entender el audio. Intenta de nuevo.');
      }
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.start();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) {
      toast.error('Por favor ingresa una descripción para el reporte.');
      return;
    }

    setCargando(true);
    try {
      const response = await aiService.generateReport(prompt, formato);

      if (formato === 'json') {
        setReporte(response.data);
      } else {
        // Para archivos binarios (Excel, PDF)
        setReporte({ tipo: formato, blob: response.data });
      }

      // Guardar en historial
      const nuevoReporte = {
        id: Date.now(),
        prompt,
        formato,
        fecha: new Date().toLocaleString(),
      };
      setHistorialReportes(prev => [nuevoReporte, ...prev].slice(0, 5)); // Mantener últimos 5

      toast.success('Reporte generado exitosamente.');
    } catch (error) {
      toast.error('Error al generar el reporte. Intenta nuevamente.');
      console.error(error);
    } finally {
      setCargando(false);
    }
  };

  const handleDownload = () => {
    if (!reporte) return;

    if (formato === 'json') {
      // Descargar JSON
      const blob = new Blob([JSON.stringify(reporte, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `reporte_${new Date().toISOString().split('T')[0]}.json`;
      link.click();
      URL.revokeObjectURL(url);
      toast.success('Reporte JSON descargado');
    } else if (reporte.blob) {
      // Descargar archivo binario (Excel o PDF)
      const url = URL.createObjectURL(reporte.blob);
      const link = document.createElement('a');
      link.href = url;
      const extension = formato === 'excel' ? 'xlsx' : 'pdf';
      link.download = `reporte_${new Date().toISOString().split('T')[0]}.${extension}`;
      link.click();
      URL.revokeObjectURL(url);
      toast.success(`Reporte ${formato.toUpperCase()} descargado`);
    }
  };

  const seleccionarPlantilla = (plantilla) => {
    setPrompt(plantilla.prompt);
    setMostrarPlantillas(false);
    toast.success('Plantilla aplicada');
  };

  const copiarPrompt = (texto) => {
    navigator.clipboard.writeText(texto);
    toast.success('Prompt copiado al portapapeles');
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <FileText className="mr-3 text-green-600" size={32} />
          <h1 className="text-2xl font-bold text-gray-800">Generar Reportes con IA</h1>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => setMostrarPlantillas(!mostrarPlantillas)}
            className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 flex items-center transition-colors"
          >
            <Sparkles className="mr-2" size={16} />
            Plantillas
          </button>
          {historialReportes.length > 0 && (
            <button
              onClick={() => setMostrarVistaPrevia(!mostrarVistaPrevia)}
              className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 flex items-center transition-colors"
            >
              <History className="mr-2" size={16} />
              Historial
            </button>
          )}
        </div>
      </div>

      {/* Panel de Plantillas */}
      {mostrarPlantillas && (
        <div className="mb-6 p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border-2 border-purple-200">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold text-gray-800 flex items-center">
              <Sparkles className="mr-2 text-purple-600" size={20} />
              Plantillas de Reportes
            </h3>
            <button onClick={() => setMostrarPlantillas(false)} className="text-gray-500 hover:text-gray-700">
              <X size={20} />
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {PLANTILLAS_PROMPT.map((plantilla, index) => (
              <div
                key={index}
                className="bg-white p-4 rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer border border-gray-200 hover:border-purple-400"
                onClick={() => seleccionarPlantilla(plantilla)}
              >
                <h4 className="font-semibold text-gray-800 mb-1">{plantilla.titulo}</h4>
                <p className="text-sm text-gray-600 mb-2">{plantilla.descripcion}</p>
                <p className="text-xs text-gray-500 italic line-clamp-2">{plantilla.prompt}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Panel de Historial */}
      {mostrarVistaPrevia && historialReportes.length > 0 && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg border-2 border-gray-200">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold text-gray-800 flex items-center">
              <History className="mr-2 text-gray-600" size={20} />
              Historial de Reportes
            </h3>
            <button onClick={() => setMostrarVistaPrevia(false)} className="text-gray-500 hover:text-gray-700">
              <X size={20} />
            </button>
          </div>
          <div className="space-y-2">
            {historialReportes.map((item) => (
              <div key={item.id} className="bg-white p-3 rounded border border-gray-200 hover:border-gray-300 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="text-sm text-gray-700 font-medium">{item.prompt}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {item.formato.toUpperCase()} - {item.fecha}
                    </p>
                  </div>
                  <button
                    onClick={() => copiarPrompt(item.prompt)}
                    className="ml-2 p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
                  >
                    <Copy size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="mb-6">
        <div className="mb-4">
          <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 mb-2">
            Descripción del Reporte (en lenguaje natural)
          </label>
          <div className="relative">
            <textarea
              id="prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 pr-20"
              placeholder="Ej: Genera un reporte de ventas del último mes con totales por producto en formato Excel"
              rows={4}
              required
            />
            {prompt && (
              <button
                type="button"
                onClick={() => setPrompt('')}
                className="absolute top-2 right-2 text-gray-400 hover:text-gray-600"
                title="Limpiar texto"
              >
                <X size={20} />
              </button>
            )}
            {/* Botón de micrófono desactivado temporalmente
            <button
              type="button"
              onClick={handleVoiceInput}
              className={`absolute top-2 right-2 transition-colors ${isListening ? 'text-red-500 animate-pulse' : 'text-gray-400 hover:text-green-600'}`}
              title="Usar micrófono"
            >
              {isListening ? <MicOff size={20} /> : <Mic size={20} />}
            </button>
            */}
          </div>
          <p className="text-xs text-gray-500 mt-1">
            💡 Tip: Describe claramente qué datos necesitas, el período de tiempo, y el formato deseado
          </p>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <label htmlFor="formato" className="block text-sm font-medium text-gray-700 mb-2">
              Formato del Reporte
            </label>
            <select
              id="formato"
              value={formato}
              onChange={(e) => setFormato(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              <option value="json">JSON (Vista en Pantalla)</option>
              <option value="excel">Excel (.xlsx)</option>
              <option value="pdf">PDF (.pdf)</option>
            </select>
          </div>
          <div className="flex items-end">
            <button
              type="submit"
              disabled={cargando}
              className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center transition-colors"
            >
              {cargando ? (
                <>
                  <Loader className="animate-spin mr-2" size={16} />
                  Generando...
                </>
              ) : (
                <>
                  <File className="mr-2" size={16} />
                  Generar Reporte
                </>
              )}
            </button>
          </div>
        </div>
      </form>

      {/* Barra de progreso cuando está cargando */}
      {cargando && (
        <div className="mb-6">
          <div className="bg-gray-200 rounded-full h-2 overflow-hidden">
            <div className="bg-green-600 h-full animate-pulse" style={{ width: '100%' }}></div>
          </div>
          <p className="text-sm text-gray-600 text-center mt-2">
            La IA está procesando tu solicitud y consultando la base de datos...
          </p>
        </div>
      )}

      {reporte && !cargando && (
        <div className="mt-6 bg-gradient-to-br from-green-50 to-blue-50 p-6 rounded-lg border-2 border-green-200">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-800 flex items-center">
              <Download className="mr-2 text-green-600" size={20} />
              Reporte Generado
            </h2>
            <button
              onClick={handleDownload}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 flex items-center transition-colors shadow-md"
            >
              <Download className="mr-2" size={16} />
              Descargar
            </button>
          </div>

          {formato === 'json' ? (
            <div className="bg-white p-4 rounded-md overflow-x-auto border border-gray-300 shadow-inner max-h-96">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-gray-700">Vista Previa JSON</span>
                <button
                  onClick={() => copiarPrompt(JSON.stringify(reporte, null, 2))}
                  className="text-sm text-blue-600 hover:text-blue-800 flex items-center"
                >
                  <Copy size={14} className="mr-1" />
                  Copiar
                </button>
              </div>
              <pre className="text-sm text-gray-800 font-mono">{JSON.stringify(reporte, null, 2)}</pre>
            </div>
          ) : (
            <div className="bg-white p-6 rounded-md border border-gray-300 shadow-inner">
              <div className="flex flex-col items-center space-y-4">
                <div className="p-4 bg-green-100 rounded-full">
                  <FileText className="text-green-600" size={48} />
                </div>
                <div className="text-center">
                  <p className="text-lg font-semibold text-gray-800">
                    Reporte {formato.toUpperCase()} generado exitosamente
                  </p>
                  <p className="text-sm text-gray-600 mt-1">
                    El archivo está listo para descargar. Haz clic en el botón de arriba.
                  </p>
                </div>
                <div className="flex items-center space-x-2 text-sm text-gray-500">
                  <Eye size={16} />
                  <span>Formato: {formato === 'excel' ? 'Microsoft Excel (.xlsx)' : 'Adobe PDF (.pdf)'}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Ayuda y ejemplos */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <h3 className="text-sm font-semibold text-blue-900 mb-2">📚 Ejemplos de prompts:</h3>
        <ul className="text-xs text-blue-800 space-y-1">
          <li>• "Reporte de ventas totales por mes del año 2024"</li>
          <li>• "Lista de los 20 clientes con mayor volumen de compras"</li>
          <li>• "Análisis de productos con stock menor a 10 unidades"</li>
          <li>• "Resumen de ingresos y gastos del último trimestre"</li>
          <li>• "Reporte de pedidos pendientes de entrega"</li>
        </ul>
      </div>
    </div>
  );
}