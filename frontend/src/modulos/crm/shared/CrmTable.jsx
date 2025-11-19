import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, Edit, Trash2 } from 'lucide-react';
import { formatDateForDisplay } from '../../../utils/errorHandler';

const CrmTable = ({ columns, data, onEdit, onDelete, customActions, itemsPerPage = 10 }) => {
  const [currentPage, setCurrentPage] = useState(1);

  if (!data || !Array.isArray(data)) {
    return <div className="text-center py-8 text-gray-500">No hay datos para mostrar</div>;
  }

  if (data.length === 0) {
    return <div className="text-center py-8 text-gray-500">No se encontraron registros</div>;
  }

  const totalPages = Math.ceil(data.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedData = data.slice(startIndex, startIndex + itemsPerPage);

  /**
   * Renderiza el contenido de una celda con soporte para render customizado
   */
  const renderCell = (item, column) => {
    // Si hay función de render personalizada, usarla
    if (column.render && typeof column.render === 'function') {
      return column.render(item);
    }

    // Obtener el valor usando el key
    const value = item[column.key];

    // Manejar valores null/undefined
    if (value === null || value === undefined) {
      return <span className="text-gray-400">N/A</span>;
    }

    // Manejar objetos (nested data)
    if (typeof value === 'object' && !Array.isArray(value)) {
      // Si es un objeto con propiedades comunes, intentar mostrar algo útil
      if (value.email) return value.email;
      if (value.nombre) return value.nombre;
      if (value.name) return value.name;
      return <span className="text-gray-400">[Objeto]</span>;
    }

    // Manejar arrays
    if (Array.isArray(value)) {
      return value.length > 0 ? value.join(', ') : <span className="text-gray-400">-</span>;
    }

    // Manejar fechas (formato ISO)
    if (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}/.test(value)) {
      return formatDateForDisplay(value, value.includes('T'));
    }

    // Manejar booleanos
    if (typeof value === 'boolean') {
      return value ? '✓' : '✗';
    }

    // Valor normal (string, number)
    return value;
  };

  return (
    <div>
      <table className="min-w-full bg-white border">
        <thead>
          <tr>
            {columns.map((col, idx) => (
              <th key={idx} className="py-2 px-4 border-b text-left">{col.header}</th>
            ))}
            <th className="py-2 px-4 border-b">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {paginatedData.map((item, idx) => (
            <tr key={item.id || idx} className="hover:bg-gray-50">
              {columns.map((col, colIdx) => (
                <td key={colIdx} className="py-2 px-4 border-b">
                  {renderCell(item, col)}
                </td>
              ))}
              <td className="py-2 px-4 border-b">
                {customActions ? customActions(item) : (
                  <div className="flex gap-2">
                    {onEdit && (
                      <button 
                        onClick={() => onEdit(item)} 
                        className="text-blue-500 hover:text-blue-700"
                        title="Editar"
                      >
                        <Edit size={16} />
                      </button>
                    )}
                    {onDelete && (
                      <button 
                        onClick={() => onDelete(item.id)} 
                        className="text-red-500 hover:text-red-700"
                        title="Eliminar"
                      >
                        <Trash2 size={16} />
                      </button>
                    )}
                  </div>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="flex justify-between items-center mt-4">
        <button
          onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
          disabled={currentPage === 1}
          className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
        >
          <ChevronLeft size={16} />
        </button>
        <span>Página {currentPage} de {totalPages}</span>
        <button
          onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
          disabled={currentPage === totalPages}
          className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50"
        >
          <ChevronRight size={16} />
        </button>
      </div>
    </div>
  );
};

export default CrmTable;