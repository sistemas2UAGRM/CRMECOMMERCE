import React, { useState, useEffect } from 'react';
import { MessageSquare } from 'lucide-react';
import { listarTickets, actualizarTicketParcial, responderTicket } from '../../../services/soporteService';
import CrmTable from '../shared/CrmTable';
import CrmFilters from '../shared/CrmFilters';
import CrmModal from '../shared/CrmModal';
import MensajeForm from './MensajeForm';
import toast from 'react-hot-toast';

const GestionSoporte = () => {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({});
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedTicket, setSelectedTicket] = useState(null);

  useEffect(() => {
    fetchTickets();
  }, [filters]);

  const fetchTickets = async () => {
    try {
      const data = await listarTickets(filters);
      setTickets(data.results || data || []);
    } catch (error) {
      toast.error('Error al cargar tickets');
    } finally {
      setLoading(false);
    }
  };

  const handleRespond = (ticket) => {
    setSelectedTicket(ticket);
    setModalOpen(true);
  };

  const handleUpdateStatus = async (id, status) => {
    try {
      await actualizarTicketParcial(id, { estado: status });
      toast.success('Estado actualizado');
      fetchTickets();
    } catch (error) {
      toast.error('Error al actualizar');
    }
  };

  const handleSaveResponse = async (data) => {
    try {
      await responderTicket(selectedTicket.id, data);
      toast.success('Respuesta enviada');
      setModalOpen(false);
      fetchTickets();
    } catch (error) {
      toast.error('Error al responder');
    }
  };

  const columns = [
    { header: 'Asunto', key: 'asunto' },
    { header: 'Cliente', key: 'cliente' },
    { header: 'Estado', key: 'estado' },
    { header: 'Prioridad', key: 'prioridad' },
    { header: 'Fecha', key: 'fecha_creacion' },
  ];

  const actions = (ticket) => (
    <div className="flex gap-2">
      <button onClick={() => handleRespond(ticket)} className="text-blue-500">
        <MessageSquare size={16} />
      </button>
      <select onChange={(e) => handleUpdateStatus(ticket.id, e.target.value)} defaultValue={ticket.estado}>
        <option value="abierto">Abierto</option>
        <option value="en_proceso">En Proceso</option>
        <option value="resuelto">Resuelto</option>
      </select>
    </div>
  );

  if (loading) return <div>Cargando...</div>;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Gestión de Soporte</h1>
      <CrmFilters filters={filters} onFilterChange={setFilters} placeholder="Buscar tickets..." />
      <CrmTable
        columns={columns}
        data={tickets}
        customActions={actions}
      />
      <CrmModal isOpen={modalOpen} onClose={() => setModalOpen(false)} title="Responder Ticket">
        <MensajeForm onSave={handleSaveResponse} onCancel={() => setModalOpen(false)} />
      </CrmModal>
    </div>
  );
};

export default GestionSoporte;