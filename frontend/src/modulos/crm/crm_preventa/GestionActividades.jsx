import React, { useState, useEffect } from 'react';
import { Plus } from 'lucide-react';
import { listarActividades, crearActividad, actualizarActividad, eliminarActividad } from '../../../services/crmPreventaService';
import CrmTable from '../shared/CrmTable';
import CrmFilters from '../shared/CrmFilters';
import CrmModal from '../shared/CrmModal';
import ActividadForm from './ActividadForm';
import toast from 'react-hot-toast';

const GestionActividades = () => {
  const [actividades, setActividades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({});
  const [modalOpen, setModalOpen] = useState(false);
  const [editingActividad, setEditingActividad] = useState(null);

  useEffect(() => {
    fetchActividades();
  }, [filters]);

  const fetchActividades = async () => {
    try {
      const data = await listarActividades(filters);
      setActividades(data.results || data || []);
    } catch (error) {
      toast.error('Error al cargar actividades');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingActividad(null);
    setModalOpen(true);
  };

  const handleEdit = (actividad) => {
    setEditingActividad(actividad);
    setModalOpen(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar actividad?')) return;
    try {
      await eliminarActividad(id);
      toast.success('Actividad eliminada');
      fetchActividades();
    } catch (error) {
      toast.error('Error al eliminar');
    }
  };

  const handleSave = async (data) => {
    try {
      if (editingActividad) {
        await actualizarActividad(editingActividad.id, data);
        toast.success('Actividad actualizada');
      } else {
        await crearActividad(data);
        toast.success('Actividad creada');
      }
      setModalOpen(false);
      fetchActividades();
    } catch (error) {
      toast.error('Error al guardar');
    }
  };

  const columns = [
    { header: 'Tipo', key: 'tipo' },
    { header: 'Notas', key: 'notas' },
    { header: 'Relacionado', key: 'related_object' },
    { header: 'ID Relacionado', key: 'related_id' },
  ];

  if (loading) return <div>Cargando...</div>;

  return (
    <div>
      <CrmFilters filters={filters} onFilterChange={setFilters} placeholder="Buscar actividades..." />
      <button onClick={handleCreate} className="mb-4 bg-blue-500 text-white px-4 py-2 rounded flex items-center">
        <Plus size={16} className="mr-2" /> Nueva Actividad
      </button>
      <CrmTable
        columns={columns}
        data={actividades}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
      <CrmModal isOpen={modalOpen} onClose={() => setModalOpen(false)} title={editingActividad ? 'Editar Actividad' : 'Nueva Actividad'}>
        <ActividadForm initialData={editingActividad} onSave={handleSave} onCancel={() => setModalOpen(false)} />
      </CrmModal>
    </div>
  );
};

export default GestionActividades;