import React, { useState, useEffect } from 'react';
import { Plus } from 'lucide-react';
import { listarSegmentos, crearSegmento, actualizarSegmento, eliminarSegmento } from '../../../services/clientesService';
import CrmTable from '../shared/CrmTable';
import CrmFilters from '../shared/CrmFilters';
import CrmModal from '../shared/CrmModal';
import SegmentoForm from './SegmentoForm';
import toast from 'react-hot-toast';

const GestionSegmentosTable = () => {
  const [segmentos, setSegmentos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({});
  const [modalOpen, setModalOpen] = useState(false);
  const [editingSegmento, setEditingSegmento] = useState(null);

  useEffect(() => {
    fetchSegmentos();
  }, [filters]);

  const fetchSegmentos = async () => {
    try {
      const data = await listarSegmentos(filters);
      setSegmentos(data.results || data || []);
    } catch (error) {
      toast.error('Error al cargar segmentos');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingSegmento(null);
    setModalOpen(true);
  };

  const handleEdit = (segmento) => {
    setEditingSegmento(segmento);
    setModalOpen(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar segmento?')) return;
    try {
      await eliminarSegmento(id);
      toast.success('Segmento eliminado');
      fetchSegmentos();
    } catch (error) {
      toast.error('Error al eliminar');
    }
  };

  const handleSave = async (data) => {
    try {
      if (editingSegmento) {
        await actualizarSegmento(editingSegmento.id, data);
        toast.success('Segmento actualizado');
      } else {
        await crearSegmento(data);
        toast.success('Segmento creado');
      }
      setModalOpen(false);
      fetchSegmentos();
    } catch (error) {
      toast.error('Error al guardar');
    }
  };

  const columns = [
    { header: 'Nombre', key: 'nombre' },
    { header: 'Descripción', key: 'descripcion' },
  ];

  if (loading) return <div>Cargando...</div>;

  return (
    <div>
      <CrmFilters filters={filters} onFilterChange={setFilters} placeholder="Buscar segmentos..." />
      <button onClick={handleCreate} className="mb-4 bg-blue-500 text-white px-4 py-2 rounded flex items-center">
        <Plus size={16} className="mr-2" /> Nuevo Segmento
      </button>
      <CrmTable
        columns={columns}
        data={segmentos}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
      <CrmModal isOpen={modalOpen} onClose={() => setModalOpen(false)} title={editingSegmento ? 'Editar Segmento' : 'Nuevo Segmento'}>
        <SegmentoForm initialData={editingSegmento} onSave={handleSave} onCancel={() => setModalOpen(false)} />
      </CrmModal>
    </div>
  );
};

export default GestionSegmentosTable;