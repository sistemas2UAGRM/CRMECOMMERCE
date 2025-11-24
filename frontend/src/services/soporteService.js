import api from "./api";

const ENDPOINT_TICKETS = "/crm/soporte/admin/tickets/";

const listarTickets = async (params = {}) => {
  const res = await api.get(ENDPOINT_TICKETS, { params });
  return res.data;
};

const detalleTicket = async (id) => {
  const res = await api.get(`${ENDPOINT_TICKETS}${id}/`);
  return res.data;
};

const actualizarTicketParcial = async (id, data) => {
  const res = await api.patch(`${ENDPOINT_TICKETS}${id}/`, data);
  return res.data;
};

const responderTicket = async (ticketId, data) => {
  const res = await api.post(`/crm/soporte/tickets/${ticketId}/responder/`, data);
  return res.data;
};

export {
  listarTickets,
  detalleTicket,
  actualizarTicketParcial,
  responderTicket,
};