// src/modulos/productos/ProductoTable.jsx
import React from "react";

/*
 Props:
  - productos: array de productos
  - onVer(producto)
  - onEditar(producto)
  - onEliminar(id)
  - cargando: boolean
*/
export default function ProductoTable({ productos = [], onVer, onEditar, onEliminar, cargando }) {
  return (
    <div className="bg-white shadow rounded overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">#</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nombre</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider hidden sm:table-cell">SKU</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Precio</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider hidden md:table-cell">Categorías</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stock</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Activo</th>
            <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
          </tr>
        </thead>

        <tbody className="bg-white divide-y divide-gray-200">
          {cargando ? (
            <tr>
              <td colSpan="8" className="px-4 py-6 text-center text-gray-500">Cargando productos...</td>
            </tr>
          ) : (productos && productos.length ? (
            productos.map((p, idx) => (
              <tr key={p.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm text-gray-700">{idx + 1}</td>
                <td className="px-4 py-3 text-sm text-gray-800">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gray-100 rounded overflow-hidden">
                      <img
                        src={(p.imagenes && p.imagenes.length && (p.imagenes.find(i => i.es_principal)?.imagen || p.imagenes[0].imagen)) || p.imagen || "/placeholder.png"}
                        alt={p.nombre}
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <div>
                      <div className="font-medium">{p.nombre}</div>
                      <div className="text-xs text-gray-500 hidden md:block truncate max-w-xs">{p.descripcion}</div>
                    </div>
                  </div>
                </td>

                <td className="px-4 py-3 text-sm text-gray-600 hidden sm:table-cell">{p.codigo ?? "-"}</td>

                <td className="px-4 py-3 text-sm text-gray-800">Bs {p.precio ?? "-"}</td>

                <td className="px-4 py-3 text-sm text-gray-600 hidden md:table-cell">
                  {(p.categorias || []).map(c => c.nombre).join(", ") || "-"}
                </td>

                <td className="px-4 py-3 text-sm text-gray-700">{p.stock_total ?? 0}</td>

                <td className="px-4 py-3 text-sm">
                  {p.activo ? <span className="inline-block px-2 py-0.5 text-xs bg-green-100 text-green-800 rounded">Sí</span>
                              : <span className="inline-block px-2 py-0.5 text-xs bg-red-100 text-red-800 rounded">No</span>}
                </td>

                <td className="px-4 py-3 text-right text-sm">
                  <div className="inline-flex items-center space-x-2">
                    <button onClick={() => onVer(p)} className="px-2 py-1 text-xs border rounded hover:bg-gray-100">Ver</button>
                    <button onClick={() => onEditar(p)} className="px-2 py-1 text-xs bg-indigo-600 text-white rounded hover:bg-indigo-700">Editar</button>
                    <button onClick={() => onEliminar(p.id)} className="px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700">Eliminar</button>
                  </div>
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="8" className="px-4 py-6 text-center text-gray-500">No hay productos para mostrar.</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
