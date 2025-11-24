import React, { useState, useEffect } from 'react';

const PotencialForm = ({ initialData, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    nombre_completo: '',
    email: '',
    telefono: '',
    empresa: '',
    fuente: '',
    estado: '',
    propietario_id: '',
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
        <label className="block text-sm font-medium mb-1">Nombre Completo *</label>
        <input
          type="text"
          name="nombre_completo"
          value={formData.nombre_completo}
          onChange={handleChange}
          className="w-full border px-3 py-2 rounded"
          placeholder="Ej: Juan Pérez"
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
          placeholder="Ej: juan@empresa.com"
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
          placeholder="Ej: Acme Corp"
        />
      </div>
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Fuente *</label>
        <select
          name="fuente"
          value={formData.fuente}
          onChange={handleChange}
          className="w-full border px-3 py-2 rounded"
          required
        >
          <option value="">Seleccionar origen del lead</option>
          <option value="INSTAGRAM">Instagram</option>
          <option value="FACEBOOK">Facebook</option>
          <option value="LINKEDIN">LinkedIn</option>
          <option value="WEB">Página Web</option>
          <option value="REFERIDO">Referido</option>
          <option value="OTRO">Otro</option>
        </select>
      </div>
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Estado</label>
        <select
          name="estado"
          value={formData.estado}
          onChange={handleChange}
          className="w-full border px-3 py-2 rounded"
          required
        >
          <option value="">Seleccionar</option>
          <option value="NUEVO">Nuevo</option>
          <option value="CONTACTADO">Contactado</option>
          <option value="CALIFICADO">Calificado</option>
          <option value="DESCARTADO">Descartado</option>
        </select>
      </div>
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Notas</label>
        <textarea
          name="notas"
          value={formData.notas}
          onChange={handleChange}
          className="w-full border px-3 py-2 rounded"
        />
      </div>
      <div className="flex justify-end gap-2">
        <button type="button" onClick={onCancel} className="px-4 py-2 bg-gray-300 rounded">Cancelar</button>
        <button type="submit" className="px-4 py-2 bg-blue-500 text-white rounded">Guardar</button>
      </div>
    </form>
  );
};

export default PotencialForm;