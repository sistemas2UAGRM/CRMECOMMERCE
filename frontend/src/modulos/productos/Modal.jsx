// src/modulos/productos/Modal.jsx
import React from "react";

export default function Modal({ abierto, titulo, onCerrar, children }) {
  if (!abierto) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="bg-white rounded-lg shadow-lg max-w-3xl w-full">
        <div className="flex justify-between items-center p-4 border-b">
          <h3 className="text-lg font-semibold">{titulo}</h3>
          <button onClick={onCerrar} className="text-gray-600 hover:text-gray-800">Cerrar</button>
        </div>
        <div className="p-4">
          {children}
        </div>
      </div>
    </div>
  );
}
