import React from "react";

export default function AlmacenTable({ almacenes = [], onEditar, onEliminar, onVerInventario, cargando }) {
  return (
    <div className="bg-white shadow rounded overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Nombre</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Código</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Dirección</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Teléfono</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Activo</th>
            <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">Acciones</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {cargando ? (
            <tr><td colSpan="5" className="p-6 text-center text-gray-500">Cargando almacenes...</td></tr>
          ) : almacenes.length > 0 ? (
            almacenes.map((almacen) => (
              <tr key={almacen.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium">{almacen.nombre}</td>
                <td className="px-4 py-3 text-sm text-gray-600">{almacen.codigo}</td>
                <td className="px-4 py-3 text-sm text-gray-600">{almacen.direccion || "-"}</td>
                <td className="px-4 py-3 text-sm text-gray-600">{almacen.telefono || "-"}</td>
                <td className="px-4 py-3 text-sm">
                  {almacen.activo ? 
                    <span className="px-2 py-0.5 text-xs bg-green-100 text-green-800 rounded">Sí</span> :
                    <span className="px-2 py-0.5 text-xs bg-red-100 text-red-800 rounded">No</span>
                  }
                </td>
                <td className="px-4 py-3 text-right text-sm">
                  <div className="inline-flex items-center space-x-2">
                    <button onClick={() => onVerInventario(almacen)} className="px-2 py-1 text-xs border rounded hover:bg-gray-100">Inventario</button>
                    <button onClick={() => onEditar(almacen)} className="px-2 py-1 text-xs bg-indigo-600 text-white rounded hover:bg-indigo-700">Editar</button>
                    <button onClick={() => onEliminar(almacen.id)} className="px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700">Eliminar</button>
                  </div>
                </td>
              </tr>
            ))
          ) : (
            <tr><td colSpan="6" className="p-6 text-center text-gray-500">No hay almacenes creados.</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}