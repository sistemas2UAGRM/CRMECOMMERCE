// src/modulos/productos/ProductoCard.jsx
import React from "react";

export default function ProductoCard({ producto, onVer, onEditar, onEliminar }) {
  const imagenUrl =
    producto.imagenes && producto.imagenes.length
      ? (producto.imagenes.find(img => img.es_principal)?.imagen || producto.imagenes[0].imagen)
      : producto.imagen || producto.imagen_url || "/placeholder.png";

  return (
    <div className="border rounded-lg p-3 bg-white flex flex-col">
      <div className="h-40 w-full mb-3 overflow-hidden rounded">
        <img src={imagenUrl} alt={producto.nombre} className="w-full h-full object-cover" />
      </div>
      <div className="flex-1">
        <h4 className="font-semibold text-lg">{producto.nombre}</h4>
        <p className="text-sm text-gray-500 truncate">{producto.descripcion}</p>
      </div>

      <div className="mt-3 flex items-center justify-between">
        <div>
          <div className="text-sm">Bs {producto.precio ?? "-"}</div>
          <div className="text-xs text-gray-600">Stock: {producto.stock_total ?? 0}</div>
        </div>

        <div className="flex space-x-2">
          <button onClick={() => onVer(producto)} className="px-2 py-1 text-sm rounded border">Ver</button>
          <button onClick={() => onEditar(producto)} className="px-2 py-1 text-sm rounded bg-indigo-600 text-white">Editar</button>
          <button onClick={() => onEliminar(producto.id)} className="px-2 py-1 text-sm rounded bg-red-600 text-white">Eliminar</button>
        </div>
      </div>
    </div>
  );
}
