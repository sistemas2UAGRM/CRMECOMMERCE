import React, { useState, useEffect } from 'react';
import { listarSegmentos } from '../../../services/clientesService';
import usersService from '../../../services/usersService';

const ClienteForm = ({ initialData, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    usuario_id: '',
    estado: 'NUEVO',
    segmentos_ids: [],
  });
  const [segmentos, setSegmentos] = useState([]);
  const [usuarios, setUsuarios] = useState([]);

  useEffect(() => {
    if (initialData) {
      setFormData({
        usuario_id: initialData.usuario?.id || '',
        estado: initialData.estado || '',
        segmentos_ids: initialData.segmentos?.map(s => s.id) || [],
      });
    }
    fetchSegmentos();
    fetchUsuarios();
  }, [initialData]);

  const fetchSegmentos = async () => {
    try {
      const data = await listarSegmentos();
      setSegmentos(data.results || data || []);
    } catch (error) {
      console.error('Error fetching segmentos');
    }
  };

  const fetchUsuarios = async () => {
    try {
      const data = await usersService.listar();
      setUsuarios(data.results || data || []);
    } catch (error) {
      console.error('Error fetching usuarios');
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSegmentosChange = (e) => {
    const value = Array.from(e.target.selectedOptions, option => option.value);
    setFormData({ ...formData, segmentos_ids: value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    console.log('🔍 FormData antes de validar:', formData);
    
    if (!formData.usuario_id || formData.usuario_id === '') {
      alert('Por favor selecciona un usuario.');
      console.error('❌ usuario_id vacío:', formData.usuario_id);
      return;
    }
    if (!formData.estado || formData.estado === '') {
      alert('Por favor selecciona un estado.');
      console.error('❌ estado vacío:', formData.estado);
      return;
    }
    
    // Limpiar y preparar datos
    const dataToSend = {
      usuario_id: parseInt(formData.usuario_id, 10),
      estado: formData.estado.trim(),
      segmentos_ids: Array.isArray(formData.segmentos_ids) 
        ? formData.segmentos_ids.map(id => parseInt(id, 10)).filter(id => !isNaN(id))
        : []
    };
    
    console.log('📤 Enviando datos de cliente:', dataToSend);
    console.log('✅ Tipo usuario_id:', typeof dataToSend.usuario_id, '| Valor:', dataToSend.usuario_id);
    console.log('✅ Tipo estado:', typeof dataToSend.estado, '| Valor:', dataToSend.estado);
    console.log('✅ Segmentos:', dataToSend.segmentos_ids);
    
    // Validación final
    if (isNaN(dataToSend.usuario_id)) {
      console.error('❌ usuario_id no es un número válido');
      alert('Error: ID de usuario inválido');
      return;
    }
    
    onSave(dataToSend);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Usuario *</label>
        <select
          name="usuario_id"
          value={formData.usuario_id}
          onChange={handleChange}
          className="w-full border px-3 py-2 rounded"
          required
        >
          <option value="">Seleccionar el usuario que será cliente</option>
          {usuarios.map(user => (
            <option key={user.id} value={user.id}>
              {user.first_name} {user.last_name} - {user.email}
            </option>
          ))}
        </select>
      </div>
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Estado del Cliente *</label>
        <select
          name="estado"
          value={formData.estado}
          onChange={handleChange}
          className="w-full border px-3 py-2 rounded"
          required
        >
          <option value="">Seleccionar estado actual</option>
          <option value="NUEVO">Nuevo - Recién registrado</option>
          <option value="ACTIVO">Activo - Compras regulares</option>
          <option value="VIP">VIP - Cliente premium</option>
          <option value="RIESGO">En Riesgo - Inactividad prolongada</option>
        </select>
      </div>
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Segmentos (opcional)</label>
        <select
          multiple
          name="segmentos_ids"
          value={formData.segmentos_ids}
          onChange={handleSegmentosChange}
          className="w-full border px-3 py-2 rounded"
          size="3"
        >
          {segmentos.map(seg => (
            <option key={seg.id} value={seg.id}>{seg.nombre}</option>
          ))}
        </select>
        <p className="text-xs text-gray-500 mt-1">Mantén presionado Ctrl/Cmd para múltiples segmentos</p>
      </div>
      <div className="flex justify-end gap-2">
        <button type="button" onClick={onCancel} className="px-4 py-2 bg-gray-300 rounded">Cancelar</button>
        <button type="submit" className="px-4 py-2 bg-blue-500 text-white rounded">Guardar</button>
      </div>
    </form>
  );
};

export default ClienteForm;