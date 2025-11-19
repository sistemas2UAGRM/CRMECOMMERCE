import api from "./api";

const ENDPOINT_SEGMENTOS = "/crm/clientes/admin/segmentos/";
const ENDPOINT_CLIENTES = "/crm/clientes/admin/clientes/";

const listarSegmentos = async (params = {}) => {
  const res = await api.get(ENDPOINT_SEGMENTOS, { params });
  return res.data;
};

const detalleSegmento = async (id) => {
  const res = await api.get(`${ENDPOINT_SEGMENTOS}${id}/`);
  return res.data;
};

const crearSegmento = async (data) => {
  const res = await api.post(ENDPOINT_SEGMENTOS, data);
  return res.data;
};

const actualizarSegmento = async (id, data) => {
  const res = await api.put(`${ENDPOINT_SEGMENTOS}${id}/`, data);
  return res.data;
};

const actualizarSegmentoParcial = async (id, data) => {
  const res = await api.patch(`${ENDPOINT_SEGMENTOS}${id}/`, data);
  return res.data;
};

const eliminarSegmento = async (id) => {
  await api.delete(`${ENDPOINT_SEGMENTOS}${id}/`);
};

const listarClientes = async (params = {}) => {
  const res = await api.get(ENDPOINT_CLIENTES, { params });
  return res.data;
};

const detalleCliente = async (id) => {
  const res = await api.get(`${ENDPOINT_CLIENTES}${id}/`);
  return res.data;
};

const crearCliente = async (data) => {
  const res = await api.post(ENDPOINT_CLIENTES, data);
  return res.data;
};

const actualizarCliente = async (id, data) => {
  const res = await api.put(`${ENDPOINT_CLIENTES}${id}/`, data);
  return res.data;
};

const actualizarClienteParcial = async (id, data) => {
  const res = await api.patch(`${ENDPOINT_CLIENTES}${id}/`, data);
  return res.data;
};

const eliminarCliente = async (id) => {
  await api.delete(`${ENDPOINT_CLIENTES}${id}/`);
};

export {
  listarSegmentos,
  detalleSegmento,
  crearSegmento,
  actualizarSegmento,
  actualizarSegmentoParcial,
  eliminarSegmento,
  listarClientes,
  detalleCliente,
  crearCliente,
  actualizarCliente,
  actualizarClienteParcial,
  eliminarCliente,
};