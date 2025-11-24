import React, { useState, useEffect } from 'react';
import { listarContactos } from '../../../services/crmPreventaService';
import toast from 'react-hot-toast';

const OportunidadForm = ({ initialData, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    nombre: '',
    monto_estimado: '',
    fecha_cierre_estimada: '',
    etapa: '',
    contacto_id: '',
    propietario_id: '',
  });
  const [contactos, setContactos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (initialData) {
      setFormData({
        ...initialData,
        contacto_id: initialData.contacto?.id || '',
      });
    }
    fetchContactos();
  }, [initialData]);

  const fetchContactos = async () => {
    try {
      const data = await listarContactos();
      setContactos(data.results || data || []);
    } catch (error) {
      toast.error('Error al cargar contactos');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validar que haya contacto seleccionado
    if (!formData.contacto_id) {
      toast.error('Por favor selecciona un contacto');
      return;
    }
    
    // Preparar datos para el backend
    const dataToSend = {
      nombre: formData.nombre,
      monto_estimado: parseFloat(formData.monto_estimado),
      fecha_cierre_estimada: formData.fecha_cierre_estimada,
      etapa: formData.etapa,
      contacto_id: parseInt(formData.contacto_id, 10)
    };
    
    // Solo agregar propietario_id si existe
    if (formData.propietario_id) {
      dataToSend.propietario_id = parseInt(formData.propietario_id, 10);
    }
    
    console.log('📤 Enviando oportunidad:', dataToSend);
    onSave(dataToSend);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Nombre de la Oportunidad *</label>
        <input
          type="text"
          name="nombre"
          value={formData.nombre}
          onChange={handleChange}
          className="w-full border px-3 py-2 rounded"
          placeholder="Ej: Venta sistema CRM - Q4 2025"
          required
        />
      </div>
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Monto Estimado (Bs) *</label>
        <input
          type="number"
          name="monto_estimado"
          value={formData.monto_estimado}
          onChange={handleChange}
          className="w-full border px-3 py-2 rounded"
          placeholder="Ej: 15000"
          step="0.01"
          min="0"
          required
        />
      </div>
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Fecha Cierre Estimada *</label>
        <input
          type="date"
          name="fecha_cierre_estimada"
          value={formData.fecha_cierre_estimada}
          onChange={handleChange}
          className="w-full border px-3 py-2 rounded"
          required
        />
      </div>
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Etapa *</label>
        <select
          name="etapa"
          value={formData.etapa}
          onChange={handleChange}
          className="w-full border px-3 py-2 rounded"
          required
        >
          <option value="">Seleccionar etapa del proceso</option>
          <option value="CALIFICACION">Calificación</option>
          <option value="PROPUESTA">Propuesta Presentada</option>
          <option value="NEGOCIACION">En Negociación</option>
          <option value="GANADA">Cerrada (Ganada)</option>
          <option value="PERDIDA">Cerrada (Perdida)</option>
        </select>
      </div>
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Contacto *</label>
        {loading ? (
          <div className="text-gray-500 py-2">Cargando contactos...</div>
        ) : contactos.length === 0 ? (
          <div className="text-red-500 py-2 text-sm">
            No hay contactos disponibles. Crea uno primero en el módulo de Contactos.
          </div>
        ) : (
          <select
            name="contacto_id"
            value={formData.contacto_id}
            onChange={handleChange}
            className="w-full border px-3 py-2 rounded"
            required
          >
            <option value="">Seleccionar contacto para esta oportunidad</option>
            {contactos.map(c => (
              <option key={c.id} value={c.id}>
                {c.nombre} {c.apellido} - {c.email}
              </option>
            ))}
          </select>
        )}
      </div>
      <div className="flex justify-end gap-2">
        <button type="button" onClick={onCancel} className="px-4 py-2 bg-gray-300 rounded">Cancelar</button>
        <button type="submit" className="px-4 py-2 bg-blue-500 text-white rounded">Guardar</button>
      </div>
    </form>
  );
};

export default OportunidadForm;