import React, { useState, useEffect } from 'react';
import { Plus } from 'lucide-react';
import { listarPotenciales, crearPotencial, actualizarPotencial, eliminarPotencial } from '../../../services/crmPreventaService';
import CrmTable from '../shared/CrmTable';
import CrmFilters from '../shared/CrmFilters';
import CrmModal from '../shared/CrmModal';
import PotencialForm from './PotencialForm';
import toast from 'react-hot-toast';
import { extractErrorMessage } from '../../../utils/errorHandler';

const GestionPotenciales = () => {
  const [potenciales, setPotenciales] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({});
  const [modalOpen, setModalOpen] = useState(false);
  const [editingPotencial, setEditingPotencial] = useState(null);

  useEffect(() => {
    fetchPotenciales();
  }, [filters]);

  const fetchPotenciales = async () => {
    try {
      const data = await listarPotenciales(filters);
      setPotenciales(data.results || data || []);
    } catch (error) {
      const message = extractErrorMessage(error, 'Error al cargar potenciales');
      toast.error(message);
      console.error('Error fetching potenciales:', error.response?.data || error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingPotencial(null);
    setModalOpen(true);
  };

  const handleEdit = (potencial) => {
    setEditingPotencial(potencial);
    setModalOpen(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar potencial?')) return;
    try {
      await eliminarPotencial(id);
      toast.success('Potencial eliminado');
      fetchPotenciales();
    } catch (error) {
      const message = extractErrorMessage(error, 'Error al eliminar potencial');
      toast.error(message);
      console.error('Error deleting potencial:', error.response?.data || error);
    }
  };

  const handleSave = async (data) => {
    try {
      if (editingPotencial) {
        await actualizarPotencial(editingPotencial.id, data);
        toast.success('Potencial actualizado');
      } else {
        await crearPotencial(data);
        toast.success('Potencial creado');
      }
      setModalOpen(false);
      fetchPotenciales();
    } catch (error) {
      const message = extractErrorMessage(error, 'Error al guardar potencial');
      toast.error(message);
      console.error('Error saving potencial:', error.response?.data || error);
    }
  };

  const columns = [
    { header: 'Nombre Completo', key: 'nombre_completo' },
    { header: 'Email', key: 'email' },
    { header: 'Teléfono', key: 'telefono' },
    { header: 'Empresa', key: 'empresa' },
    { header: 'Fuente', key: 'fuente_display' },
    { header: 'Estado', key: 'estado_display' },
  ];

  if (loading) return <div>Cargando...</div>;

  return (
    <div>
      <CrmFilters filters={filters} onFilterChange={setFilters} placeholder="Buscar potenciales..." />
      <button onClick={handleCreate} className="mb-4 bg-blue-500 text-white px-4 py-2 rounded flex items-center">
        <Plus size={16} className="mr-2" /> Nuevo Potencial
      </button>
      <CrmTable
        columns={columns}
        data={potenciales}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
      <CrmModal isOpen={modalOpen} onClose={() => setModalOpen(false)} title={editingPotencial ? 'Editar Potencial' : 'Nuevo Potencial'}>
        <PotencialForm initialData={editingPotencial} onSave={handleSave} onCancel={() => setModalOpen(false)} />
      </CrmModal>
    </div>
  );
};

export default GestionPotenciales;