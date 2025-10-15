// src/modulos/productos/CategoriaForm.jsx
import React, { useState, useEffect } from "react";

export default function CategoriaForm({ categoriaInicial = null, onSubmit, onCancelar }) {
  const [datos, setDatos] = useState({ nombre: "", descripcion: "" });

  useEffect(() => {
    if (categoriaInicial) {
      setDatos({
        nombre: categoriaInicial.nombre ?? "",
        descripcion: categoriaInicial.descripcion ?? "",
      });
    }
  }, [categoriaInicial]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setDatos(prev => ({ ...prev, [name]: value }));
  };

  const submit = async (e) => {
    e.preventDefault();
    if (!datos.nombre) return alert("Nombre requerido");
    await onSubmit(datos);
  };

  return (
    <form onSubmit={submit} className="space-y-4">
      <div>
        <label className="block text-sm">Nombre</label>
        <input name="nombre" value={datos.nombre} onChange={handleChange} className="w-full border rounded p-2" />
      </div>
      <div>
        <label className="block text-sm">Descripción</label>
        <textarea name="descripcion" value={datos.descripcion} onChange={handleChange} className="w-full border rounded p-2" />
      </div>

      <div className="flex justify-end gap-2">
        <button type="button" onClick={onCancelar} className="px-4 py-2 border rounded">Cancelar</button>
        <button type="submit" className="px-4 py-2 bg-indigo-600 text-white rounded">Guardar</button>
      </div>
    </form>
  );
}
