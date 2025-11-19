import React, { useState, useEffect } from 'react';
import { Plus, Calendar, List } from 'lucide-react';
import { listarEventos, crearEvento, actualizarEvento, eliminarEvento } from '../../../services/calendarioService';
import CrmTable from '../shared/CrmTable';
import CrmFilters from '../shared/CrmFilters';
import CrmModal from '../shared/CrmModal';
import EventoForm from './EventoForm';
import toast from 'react-hot-toast';
import { extractErrorMessage } from '../../../utils/errorHandler';

const GestionCalendario = () => {
  const [eventos, setEventos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({});
  const [modalOpen, setModalOpen] = useState(false);
  const [editingEvento, setEditingEvento] = useState(null);
  const [vistaCalendario, setVistaCalendario] = useState(true);
  const [currentDate, setCurrentDate] = useState(new Date());

  useEffect(() => {
    fetchEventos();
  }, [filters]);

  const fetchEventos = async () => {
    try {
      const data = await listarEventos(filters);
      setEventos(data.results || data || []);
    } catch (error) {
      const message = extractErrorMessage(error, 'Error al cargar eventos');
      toast.error(message);
      console.error('Error fetching eventos:', error.response?.data || error);
      setEventos([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingEvento(null);
    setModalOpen(true);
  };

  const handleEdit = (evento) => {
    setEditingEvento(evento);
    setModalOpen(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar evento?')) return;
    try {
      await eliminarEvento(id);
      toast.success('Evento eliminado');
      fetchEventos();
    } catch (error) {
      const message = extractErrorMessage(error, 'Error al eliminar evento');
      toast.error(message);
      console.error('Error deleting evento:', error.response?.data || error);
    }
  };

  const handleSave = async (data) => {
    try {
      if (editingEvento) {
        await actualizarEvento(editingEvento.id, data);
        toast.success('Evento actualizado');
      } else {
        await crearEvento(data);
        toast.success('Evento creado');
      }
      setModalOpen(false);
      fetchEventos();
    } catch (error) {
      const message = extractErrorMessage(error, 'Error al guardar evento');
      toast.error(message);
      console.error('Error saving evento:', error.response?.data || error);
    }
  };

  const columns = [
    { header: 'Título', key: 'titulo' },
    { header: 'Fecha Inicio', key: 'fecha_inicio' },
    { header: 'Fecha Fin', key: 'fecha_fin' },
    { 
      header: 'Propietario', 
      key: 'propietario',
      render: (item) => item.propietario?.email || item.propietario?.first_name || 'N/A'
    },
  ];

  const renderCalendario = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    
    const monthNames = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
    const dayNames = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
    
    const dias = [];
    for (let i = 0; i < firstDay; i++) {
      dias.push(<div key={`empty-${i}`} className="h-24 border border-gray-200 bg-gray-50"></div>);
    }
    
    for (let dia = 1; dia <= daysInMonth; dia++) {
      const currentDateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(dia).padStart(2, '0')}`;
      const eventosDelDia = eventos.filter(e => {
        const fechaEvento = new Date(e.fecha_inicio).toISOString().split('T')[0];
        return fechaEvento === currentDateStr;
      });
      
      dias.push(
        <div key={dia} className="h-24 border border-gray-200 p-1 overflow-y-auto hover:bg-gray-50">
          <div className="font-bold text-sm mb-1">{dia}</div>
          {eventosDelDia.map(evento => (
            <div 
              key={evento.id}
              onClick={() => handleEdit(evento)}
              className="text-xs bg-blue-100 text-blue-800 px-1 py-0.5 rounded mb-1 cursor-pointer hover:bg-blue-200 truncate"
              title={evento.titulo}
            >
              {evento.titulo}
            </div>
          ))}
        </div>
      );
    }
    
    return (
      <div className="bg-white rounded-lg shadow">
        <div className="flex justify-between items-center p-4 border-b">
          <button 
            onClick={() => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1))}
            className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
          >
            ←
          </button>
          <h2 className="text-xl font-bold">
            {monthNames[month]} {year}
          </h2>
          <button 
            onClick={() => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1))}
            className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300"
          >
            →
          </button>
        </div>
        <div className="grid grid-cols-7 gap-0">
          {dayNames.map(day => (
            <div key={day} className="bg-gray-100 text-center font-bold py-2 border border-gray-200">
              {day}
            </div>
          ))}
          {dias}
        </div>
      </div>
    );
  };

  if (loading) return <div>Cargando...</div>;

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Gestión de Calendario</h1>
      
      <div className="flex justify-between items-center mb-4">
        <CrmFilters filters={filters} onFilterChange={setFilters} placeholder="Buscar eventos..." />
        <div className="flex gap-2">
          <button 
            onClick={() => setVistaCalendario(true)} 
            className={`px-4 py-2 rounded flex items-center ${vistaCalendario ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
          >
            <Calendar size={16} className="mr-2" /> Calendario
          </button>
          <button 
            onClick={() => setVistaCalendario(false)} 
            className={`px-4 py-2 rounded flex items-center ${!vistaCalendario ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
          >
            <List size={16} className="mr-2" /> Lista
          </button>
          <button onClick={handleCreate} className="bg-green-500 text-white px-4 py-2 rounded flex items-center">
            <Plus size={16} className="mr-2" /> Nuevo Evento
          </button>
        </div>
      </div>

      {vistaCalendario ? (
        renderCalendario()
      ) : (
        <CrmTable
          columns={columns}
          data={eventos}
          onEdit={handleEdit}
          onDelete={handleDelete}
        />
      )}

      <CrmModal isOpen={modalOpen} onClose={() => setModalOpen(false)} title={editingEvento ? 'Editar Evento' : 'Nuevo Evento'}>
        <EventoForm initialData={editingEvento} onSave={handleSave} onCancel={() => setModalOpen(false)} />
      </CrmModal>
    </div>
  );
};

export default GestionCalendario;