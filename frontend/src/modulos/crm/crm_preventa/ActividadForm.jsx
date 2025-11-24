import React, { useState, useEffect } from 'react';
import { listarPotenciales, listarContactos, listarOportunidades } from '../../../services/crmPreventaService';
import toast from 'react-hot-toast';

const ActividadForm = ({ initialData, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    tipo: '',
    notas: '',
    tipo_contenido: '',
    id_objeto: '',
  });
  const [objetosRelacionados, setObjetosRelacionados] = useState([]);
  const [loadingObjetos, setLoadingObjetos] = useState(false);

  useEffect(() => {
    if (initialData) {
      setFormData(initialData);
    }
  }, [initialData]);

  useEffect(() => {
    if (!formData.tipo_contenido) {
      setObjetosRelacionados([]);
      return;
    }

    const fetchObjetos = async () => {
      setLoadingObjetos(true);
      try {
        let data;
        if (formData.tipo_contenido === 'crm_preventa.potencial') {
          data = await listarPotenciales();
        } else if (formData.tipo_contenido === 'crm_preventa.contacto') {
          data = await listarContactos();
        } else if (formData.tipo_contenido === 'crm_preventa.oportunidad') {
          data = await listarOportunidades();
        }
        setObjetosRelacionados(data.results || data || []);
      } catch (error) {
        toast.error('Error al cargar objetos');
        console.error('Error:', error);
      } finally {
        setLoadingObjetos(false);
      }
    };

    fetchObjetos();
  }, [formData.tipo_contenido]);

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
        <label className="block text-sm font-medium mb-1">Tipo de Actividad *</label>
        <select
          name="tipo"
          value={formData.tipo}
          onChange={handleChange}
          className="w-full border px-3 py-2 rounded"
          required
        >
          <option value="">Seleccionar tipo de actividad</option>
          <option value="LLAMADA">📞 Llamada Telefónica</option>
          <option value="CORREO">📧 Correo Electrónico</option>
          <option value="WHATSAPP">💬 Mensaje WhatsApp</option>
          <option value="REUNION">🤝 Reunión</option>
          <option value="OTRO">📝 Otro</option>
        </select>
      </div>
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Notas de la Actividad *</label>
        <textarea
          name="notas"
          value={formData.notas}
          onChange={handleChange}
          className="w-full border px-3 py-2 rounded"
          placeholder="Ej: Cliente interesado en el módulo de inventarios. Solicita cotización formal y referencias de clientes. Siguiente seguimiento: presentar propuesta comercial."
          rows="4"
          required
        />
      </div>
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Relacionado con *</label>
        <select
          name="tipo_contenido"
          value={formData.tipo_contenido}
          onChange={handleChange}
          className="w-full border px-3 py-2 rounded"
          required
        >
          <option value="">Seleccionar qué tipo de registro</option>
          <option value="crm_preventa.potencial">Potencial (Lead)</option>
          <option value="crm_preventa.contacto">Contacto</option>
          <option value="crm_preventa.oportunidad">Oportunidad de Venta</option>
        </select>
      </div>
      {formData.tipo_contenido && (
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Seleccionar Objeto *</label>
          {loadingObjetos ? (
            <div className="text-gray-500 py-2">Cargando opciones...</div>
          ) : objetosRelacionados.length === 0 ? (
            <div className="text-red-500 py-2 text-sm">
              No hay registros disponibles para este tipo.
            </div>
          ) : (
            <select
              name="id_objeto"
              value={formData.id_objeto}
              onChange={handleChange}
              className="w-full border px-3 py-2 rounded"
              required
            >
              <option value="">Seleccionar...</option>
              {objetosRelacionados.map(obj => (
                <option key={obj.id} value={obj.id}>
                  {formData.tipo_contenido === 'crm_preventa.potencial' && `${obj.nombre_completo} - ${obj.email}`}
                  {formData.tipo_contenido === 'crm_preventa.contacto' && `${obj.nombre} ${obj.apellido} - ${obj.email}`}
                  {formData.tipo_contenido === 'crm_preventa.oportunidad' && `${obj.nombre} - Bs${obj.monto_estimado}`}
                </option>
              ))}
            </select>
          )}
        </div>
      )}
      <div className="flex justify-end gap-2">
        <button type="button" onClick={onCancel} className="px-4 py-2 bg-gray-300 rounded">Cancelar</button>
        <button type="submit" className="px-4 py-2 bg-blue-500 text-white rounded">Guardar</button>
      </div>
    </form>
  );
};

export default ActividadForm;