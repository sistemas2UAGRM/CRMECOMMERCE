import React, { useState, useEffect } from 'react';
import { Plus } from 'lucide-react';
import { listarOportunidades, crearOportunidad, actualizarOportunidad, eliminarOportunidad } from '../../../services/crmPreventaService';
import CrmTable from '../shared/CrmTable';
import CrmFilters from '../shared/CrmFilters';
import CrmModal from '../shared/CrmModal';
import OportunidadForm from './OportunidadForm';
import toast from 'react-hot-toast';

const GestionOportunidades = () => {
  const [oportunidades, setOportunidades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({});
  const [modalOpen, setModalOpen] = useState(false);
  const [editingOportunidad, setEditingOportunidad] = useState(null);

  useEffect(() => {
    fetchOportunidades();
  }, [filters]);

  const fetchOportunidades = async () => {
    try {
      const data = await listarOportunidades(filters);
      setOportunidades(data.results || data || []);
    } catch (error) {
      toast.error('Error al cargar oportunidades');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingOportunidad(null);
    setModalOpen(true);
  };

  const handleEdit = (oportunidad) => {
    setEditingOportunidad(oportunidad);
    setModalOpen(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar oportunidad?')) return;
    try {
      await eliminarOportunidad(id);
      toast.success('Oportunidad eliminada');
      fetchOportunidades();
    } catch (error) {
      toast.error('Error al eliminar');
    }
  };

  const handleSave = async (data) => {
    try {
      if (editingOportunidad) {
        await actualizarOportunidad(editingOportunidad.id, data);
        toast.success('Oportunidad actualizada');
      } else {
        await crearOportunidad(data);
        toast.success('Oportunidad creada');
      }
      setModalOpen(false);
      fetchOportunidades();
    } catch (error) {
      console.error('❌ Error completo:', error);
      console.error('❌ Error response:', error.response);
      console.error('❌ Error data:', error.response?.data);
      const errorMsg = error.response?.data?.detail || 
                       JSON.stringify(error.response?.data) || 
                       'Error al guardar';
      toast.error(errorMsg);
    }
  };

  const columns = [
    { header: 'Nombre', key: 'nombre' },
    { header: 'Monto Estimado', key: 'monto_estimado' },
    { header: 'Fecha Cierre', key: 'fecha_cierre_estimada' },
    { header: 'Etapa', key: 'etapa' },
    { header: 'Contacto', key: 'contacto' },
  ];

  if (loading) return <div>Cargando...</div>;

  return (
    <div>
      <CrmFilters filters={filters} onFilterChange={setFilters} placeholder="Buscar oportunidades..." />
      <button onClick={handleCreate} className="mb-4 bg-blue-500 text-white px-4 py-2 rounded flex items-center">
        <Plus size={16} className="mr-2" /> Nueva Oportunidad
      </button>
      <CrmTable
        columns={columns}
        data={oportunidades}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
      <CrmModal isOpen={modalOpen} onClose={() => setModalOpen(false)} title={editingOportunidad ? 'Editar Oportunidad' : 'Nueva Oportunidad'}>
        <OportunidadForm initialData={editingOportunidad} onSave={handleSave} onCancel={() => setModalOpen(false)} />
      </CrmModal>
    </div>
  );
};

export default GestionOportunidades;