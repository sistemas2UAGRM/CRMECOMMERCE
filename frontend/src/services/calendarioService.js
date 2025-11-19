import api from "./api";

const ENDPOINT = "/crm/calendario/eventos/";

const listarEventos = async (params = {}) => {
  const res = await api.get(ENDPOINT, { params });
  return res.data;
};

const detalleEvento = async (id) => {
  const res = await api.get(`${ENDPOINT}${id}/`);
  return res.data;
};

const crearEvento = async (data) => {
  const res = await api.post(ENDPOINT, data);
  return res.data;
};

const actualizarEvento = async (id, data) => {
  const res = await api.put(`${ENDPOINT}${id}/`, data);
  return res.data;
};

const actualizarEventoParcial = async (id, data) => {
  const res = await api.patch(`${ENDPOINT}${id}/`, data);
  return res.data;
};

const eliminarEvento = async (id) => {
  await api.delete(`${ENDPOINT}${id}/`);
};

export {
  listarEventos,
  detalleEvento,
  crearEvento,
  actualizarEvento,
  actualizarEventoParcial,
  eliminarEvento,
};