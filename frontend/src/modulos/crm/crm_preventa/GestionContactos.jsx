import React, { useState, useEffect } from 'react';
import { Plus } from 'lucide-react';
import { listarContactos, crearContacto, actualizarContacto, eliminarContacto } from '../../../services/crmPreventaService';
import CrmTable from '../shared/CrmTable';
import CrmFilters from '../shared/CrmFilters';
import CrmModal from '../shared/CrmModal';
import ContactoForm from './ContactoForm';
import toast from 'react-hot-toast';

const GestionContactos = () => {
  const [contactos, setContactos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({});
  const [modalOpen, setModalOpen] = useState(false);
  const [editingContacto, setEditingContacto] = useState(null);

  useEffect(() => {
    fetchContactos();
  }, [filters]);

  const fetchContactos = async () => {
    try {
      const data = await listarContactos(filters);
      setContactos(data.results || data || []);
    } catch (error) {
      toast.error('Error al cargar contactos');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingContacto(null);
    setModalOpen(true);
  };

  const handleEdit = (contacto) => {
    setEditingContacto(contacto);
    setModalOpen(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar contacto?')) return;
    try {
      await eliminarContacto(id);
      toast.success('Contacto eliminado');
      fetchContactos();
    } catch (error) {
      toast.error('Error al eliminar');
    }
  };

  const handleSave = async (data) => {
    try {
      if (editingContacto) {
        await actualizarContacto(editingContacto.id, data);
        toast.success('Contacto actualizado');
      } else {
        await crearContacto(data);
        toast.success('Contacto creado');
      }
      setModalOpen(false);
      fetchContactos();
    } catch (error) {
      toast.error('Error al guardar');
    }
  };

  const columns = [
    { header: 'Nombre', key: 'nombre' },
    { header: 'Apellido', key: 'apellido' },
    { header: 'Email', key: 'email' },
    { header: 'Teléfono', key: 'telefono' },
    { header: 'Empresa', key: 'empresa' },
  ];

  if (loading) return <div>Cargando...</div>;

  return (
    <div>
      <CrmFilters filters={filters} onFilterChange={setFilters} placeholder="Buscar contactos..." />
      <button onClick={handleCreate} className="mb-4 bg-blue-500 text-white px-4 py-2 rounded flex items-center">
        <Plus size={16} className="mr-2" /> Nuevo Contacto
      </button>
      <CrmTable
        columns={columns}
        data={contactos}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
      <CrmModal isOpen={modalOpen} onClose={() => setModalOpen(false)} title={editingContacto ? 'Editar Contacto' : 'Nuevo Contacto'}>
        <ContactoForm initialData={editingContacto} onSave={handleSave} onCancel={() => setModalOpen(false)} />
      </CrmModal>
    </div>
  );
};

export default GestionContactos;