// frontend/src/modulos/productos/almacenes/AlmacenForm.jsx
import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';

export default function AlmacenForm({ almacenInicial = null, onSubmit, onCancelar }) {
  const [datos, setDatos] = useState({
    nombre: '',
    codigo: '',
    direccion: '',
    telefono: '',
    activo: true,
  });

  useEffect(() => {
    if (almacenInicial) {
      setDatos({
        nombre: almacenInicial.nombre ?? '',
        codigo: almacenInicial.codigo ?? '',
        direccion: almacenInicial.direccion ?? '',
        telefono: almacenInicial.telefono ?? '',
        activo: almacenInicial.activo ?? true,
      });
    } else {
      // Resetea el formulario si no hay almacen inicial (para creación)
      setDatos({ nombre: '', codigo: '', direccion: '', telefono: '', activo: true });
    }
  }, [almacenInicial]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setDatos(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!datos.nombre || !datos.codigo) {
      return toast.error('El nombre y el código son requeridos.');
    }
    onSubmit(datos);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm">Nombre del Almacén</label>
          <input name="nombre" value={datos.nombre} onChange={handleChange} className="w-full border rounded p-2" required />
        </div>
        <div>
          <label className="block text-sm">Código / SKU</label>
          <input name="codigo" value={datos.codigo} onChange={handleChange} className="w-full border rounded p-2" required />
        </div>
        <div className="md:col-span-2">
          <label className="block text-sm">Dirección</label>
          <input name="direccion" value={datos.direccion} onChange={handleChange} className="w-full border rounded p-2" />
        </div>
        <div>
          <label className="block text-sm">Teléfono</label>
          <input name="telefono" value={datos.telefono} onChange={handleChange} className="w-full border rounded p-2" />
        </div>
        <div className="flex items-center pt-6">
          <input type="checkbox" id="activo" name="activo" checked={datos.activo} onChange={handleChange} className="h-4 w-4 rounded border-gray-300 text-indigo-600" />
          <label htmlFor="activo" className="ml-2 block text-sm">Activo</label>
        </div>
      </div>
      <div className="flex justify-end space-x-2 pt-4">
        <button type="button" onClick={onCancelar} className="px-4 py-2 rounded border">Cancelar</button>
        <button type="submit" className="px-4 py-2 rounded bg-indigo-600 text-white">Guardar Almacén</button>
      </div>
    </form>
  );
}