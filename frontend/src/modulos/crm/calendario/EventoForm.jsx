import React, { useState, useEffect } from 'react';
import { formatDateForInput } from '../../../utils/errorHandler';
import usersService from '../../../services/usersService';
import { listarContactos, listarOportunidades } from '../../../services/crmPreventaService';
import toast from 'react-hot-toast';

const EventoForm = ({ initialData, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    titulo: '',
    descripcion: '',
    fecha_inicio: '',
    fecha_fin: '',
    invitados_ids: [],
    tipo_contenido: '',
    id_objeto: '',
  });
  const [staffUsers, setStaffUsers] = useState([]);
  const [loadingStaff, setLoadingStaff] = useState(true);
  const [objetosRelacionados, setObjetosRelacionados] = useState([]);
  const [loadingObjetos, setLoadingObjetos] = useState(false);

  useEffect(() => {
    if (initialData) {
      setFormData({
        ...initialData,
        fecha_inicio: formatDateForInput(initialData.fecha_inicio),
        fecha_fin: formatDateForInput(initialData.fecha_fin),
        invitados_ids: initialData.invitados?.map(u => u.id) || [],
      });
    }
    fetchStaffUsers();
  }, [initialData]);

  useEffect(() => {
    if (!formData.tipo_contenido) {
      setObjetosRelacionados([]);
      setFormData(prev => ({ ...prev, id_objeto: '' }));
      return;
    }

    const fetchObjetos = async () => {
      setLoadingObjetos(true);
      try {
        let data;
        if (formData.tipo_contenido === 'crm_preventa.contacto') {
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

  const fetchStaffUsers = async () => {
    try {
      console.log('🔵 Cargando usuarios staff...');
      const data = await usersService.listar();
      console.log('✅ Datos recibidos:', data);
      console.log('✅ Resultados:', data.results || data);
      const allUsers = data.results || data || [];
      console.log('✅ Total usuarios:', allUsers.length);
      
      // Verificar el primer usuario para debug
      if (allUsers.length > 0) {
        console.log('🔍 Primer usuario completo:', allUsers[0]);
        console.log('🔍 Campos del primer usuario:', Object.keys(allUsers[0]));
        console.log('🔍 is_staff del primer usuario:', allUsers[0].is_staff);
      }
      
      const staff = allUsers.filter(user => user.is_staff === true);
      console.log('✅ Usuarios staff filtrados:', staff.length, staff);
      setStaffUsers(staff);
      
      if (staff.length === 0) {
        console.warn('⚠️ No hay usuarios con is_staff=true');
        console.warn('⚠️ Verifica que el backend esté devolviendo el campo is_staff');
      }
    } catch (error) {
      toast.error('Error al cargar usuarios');
      console.error('❌ Error al cargar usuarios:', error);
      console.error('❌ Error response:', error.response?.data);
    } finally {
      setLoadingStaff(false);
    }
  };

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
        <label className="block text-sm font-medium mb-1">Título del Evento *</label>
        <input
          type="text"
          name="titulo"
          value={formData.titulo}
          onChange={handleChange}
          className="w-full border px-3 py-2 rounded"
          placeholder="Ej: Reunión con cliente - Demostración producto"
          required
        />
      </div>
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Descripción</label>
        <textarea
          name="descripcion"
          value={formData.descripcion}
          onChange={handleChange}
          className="w-full border px-3 py-2 rounded"
          placeholder="Ej: Presentar funcionalidades del CRM y resolver dudas técnicas"
          rows="3"
        />
      </div>
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Fecha y Hora de Inicio *</label>
        <input
          type="datetime-local"
          name="fecha_inicio"
          value={formData.fecha_inicio}
          onChange={handleChange}
          className="w-full border px-3 py-2 rounded"
          required
        />
      </div>
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Fecha y Hora de Fin *</label>
        <input
          type="datetime-local"
          name="fecha_fin"
          value={formData.fecha_fin}
          onChange={handleChange}
          className="w-full border px-3 py-2 rounded"
          required
        />
      </div>
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Invitados (opcional)</label>
        {loadingStaff ? (
          <div className="text-gray-500 py-2">Cargando usuarios...</div>
        ) : staffUsers.length === 0 ? (
          <div className="text-red-500 py-2 text-sm">No hay usuarios disponibles</div>
        ) : (
          <>
            <select
              name="invitados_ids"
              value={formData.invitados_ids}
              onChange={(e) => {
                const options = Array.from(e.target.selectedOptions);
                const values = options.map(opt => parseInt(opt.value));
                setFormData({ ...formData, invitados_ids: values });
              }}
              className="w-full border px-3 py-2 rounded"
              multiple
              size="4"
            >
              {staffUsers.map(user => (
                <option key={user.id} value={user.id}>
                  {user.first_name} {user.last_name} - {user.email}
                </option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-1">Mantén presionado Ctrl/Cmd para seleccionar múltiples usuarios</p>
          </>
        )}
      </div>
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Relacionar con (opcional)</label>
        <select
          name="tipo_contenido"
          value={formData.tipo_contenido}
          onChange={handleChange}
          className="w-full border px-3 py-2 rounded"
        >
          <option value="">Ninguno</option>
          <option value="crm_preventa.contacto">Contacto</option>
          <option value="crm_preventa.oportunidad">Oportunidad</option>
        </select>
      </div>
      {formData.tipo_contenido && (
        <div className="mb-4">
          <label className="block text-sm font-medium mb-1">Seleccionar Objeto</label>
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
            >
              <option value="">Seleccionar...</option>
              {objetosRelacionados.map(obj => (
                <option key={obj.id} value={obj.id}>
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

export default EventoForm;