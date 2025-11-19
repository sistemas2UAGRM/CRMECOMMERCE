import React, { useState, useEffect } from 'react';
import { Plus } from 'lucide-react';
import { listarClientes, crearCliente, actualizarCliente, eliminarCliente } from '../../../services/clientesService';
import CrmTable from '../shared/CrmTable';
import CrmFilters from '../shared/CrmFilters';
import CrmModal from '../shared/CrmModal';
import ClienteForm from './ClienteForm';
import toast from 'react-hot-toast';
import { extractErrorMessage } from '../../../utils/errorHandler';

const GestionClientesTable = () => {
  const [clientes, setClientes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({});
  const [modalOpen, setModalOpen] = useState(false);
  const [editingCliente, setEditingCliente] = useState(null);

  useEffect(() => {
    fetchClientes();
  }, [filters]);

  const fetchClientes = async () => {
    try {
      const data = await listarClientes(filters);
      setClientes(data.results || data || []);
    } catch (error) {
      const message = extractErrorMessage(error, 'Error al cargar clientes');
      toast.error(message);
      console.error('Error fetching clientes:', error.response?.data || error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingCliente(null);
    setModalOpen(true);
  };

  const handleEdit = (cliente) => {
    setEditingCliente(cliente);
    setModalOpen(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar cliente?')) return;
    try {
      await eliminarCliente(id);
      toast.success('Cliente eliminado');
      fetchClientes();
    } catch (error) {
      const message = extractErrorMessage(error, 'Error al eliminar cliente');
      toast.error(message);
      console.error('Error deleting cliente:', error.response?.data || error);
    }
  };

  const handleSave = async (data) => {
    console.log('🔵 GestionClientesTable - handleSave llamado con:', data);
    try {
      if (editingCliente) {
        console.log('✏️ Modo edición - ID:', editingCliente.id);
        await actualizarCliente(editingCliente.id, data);
        toast.success('Cliente actualizado');
      } else {
        console.log('➕ Modo creación - Llamando crearCliente...');
        const response = await crearCliente(data);
        console.log('✅ Cliente creado exitosamente:', response);
        toast.success('Cliente creado');
      }
      setModalOpen(false);
      fetchClientes();
    } catch (error) {
      console.error('❌ Error completo:', error);
      console.error('❌ Error response:', error.response);
      console.error('❌ Error data:', error.response?.data);
      const message = extractErrorMessage(error, 'Error al guardar cliente');
      toast.error(message);
    }
  };

  const columns = [
    { 
      header: 'Usuario', 
      key: 'usuario',
      render: (item) => item.usuario?.email || item.usuario?.first_name || 'N/A'
    },
    { 
      header: 'Estado', 
      key: 'estado_display'
    },
    { 
      header: 'Total Gastado', 
      key: 'total_gastado',
      render: (item) => `$${parseFloat(item.total_gastado || 0).toFixed(2)}`
    },
    { 
      header: 'Total Pedidos', 
      key: 'total_pedidos'
    },
    { 
      header: 'Última Compra', 
      key: 'fecha_ultima_compra'
    },
  ];

  if (loading) return <div>Cargando...</div>;

  return (
    <div>
      <CrmFilters filters={filters} onFilterChange={setFilters} placeholder="Buscar clientes..." />
      <button onClick={handleCreate} className="mb-4 bg-blue-500 text-white px-4 py-2 rounded flex items-center">
        <Plus size={16} className="mr-2" /> Nuevo Cliente
      </button>
      <CrmTable
        columns={columns}
        data={clientes}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
      <CrmModal isOpen={modalOpen} onClose={() => setModalOpen(false)} title={editingCliente ? 'Editar Cliente' : 'Nuevo Cliente'}>
        <ClienteForm initialData={editingCliente} onSave={handleSave} onCancel={() => setModalOpen(false)} />
      </CrmModal>
    </div>
  );
};

export default GestionClientesTable;