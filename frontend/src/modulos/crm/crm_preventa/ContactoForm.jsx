import React, { useState, useEffect } from 'react';

const ContactoForm = ({ initialData, onSave, onCancel, potenciales = [] }) => {
  const [formData, setFormData] = useState({
    nombre: '',
    apellido: '',
    email: '',
    telefono: '',
    empresa: '',
    potencial_origen: '',
  });

  useEffect(() => {
    if (initialData) {
      setFormData(initialData);
    }
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Nombre *</label>
        <input
          type="text"
          name="nombre"
          value={formData.nombre}
          onChange={handleChange}
          className="w-full border px-3 py-2 rounded"
          placeholder="Ej: Juan"
          required
        />
      </div>
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Apellido *</label>
        <input
          type="text"
          name="apellido"
          value={formData.apellido}
          onChange={handleChange}
          className="w-full border px-3 py-2 rounded"
          placeholder="Ej: Pérez"
          required
        />
      </div>
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Email *</label>
        <input
          type="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          className="w-full border px-3 py-2 rounded"
          placeholder="Ej: juan.perez@empresa.com"
          required
        />
      </div>
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Teléfono</label>
        <input
          type="text"
          name="telefono"
          value={formData.telefono}
          onChange={handleChange}
          className="w-full border px-3 py-2 rounded"
          placeholder="Ej: +591 12345678"
        />
      </div>
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Empresa</label>
        <input
          type="text"
          name="empresa"
          value={formData.empresa}
          onChange={handleChange}
          className="w-full border px-3 py-2 rounded"
          placeholder="Ej: Tech Solutions SA"
        />
      </div>
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Potencial Origen (opcional)</label>
        <select
          name="potencial_origen"
          value={formData.potencial_origen}
          onChange={handleChange}
          className="w-full border px-3 py-2 rounded"
        >
          <option value="">Ninguno - Contacto directo</option>
          {potenciales.map(p => (
            <option key={p.id} value={p.id}>
              {p.nombre_completo} - {p.email}
            </option>
          ))}
        </select>
      </div>
      <div className="flex justify-end gap-2">
        <button type="button" onClick={onCancel} className="px-4 py-2 bg-gray-300 rounded">Cancelar</button>
        <button type="submit" className="px-4 py-2 bg-blue-500 text-white rounded">Guardar</button>
      </div>
    </form>
  );
};

export default ContactoForm;