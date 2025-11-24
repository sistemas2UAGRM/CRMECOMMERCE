import api from "./api";

const ENDPOINT_POTENCIALES = "/crm/crm_preventa/potenciales/";
const ENDPOINT_CONTACTOS = "/crm/crm_preventa/contactos/";
const ENDPOINT_OPORTUNIDADES = "/crm/crm_preventa/oportunidades/";
const ENDPOINT_ACTIVIDADES = "/crm/crm_preventa/actividades/";

const listarPotenciales = async (params = {}) => {
  const res = await api.get(ENDPOINT_POTENCIALES, { params });
  return res.data;
};

const detallePotencial = async (id) => {
  const res = await api.get(`${ENDPOINT_POTENCIALES}${id}/`);
  return res.data;
};

const crearPotencial = async (data) => {
  const res = await api.post(ENDPOINT_POTENCIALES, data);
  return res.data;
};

const actualizarPotencial = async (id, data) => {
  const res = await api.put(`${ENDPOINT_POTENCIALES}${id}/`, data);
  return res.data;
};

const actualizarPotencialParcial = async (id, data) => {
  const res = await api.patch(`${ENDPOINT_POTENCIALES}${id}/`, data);
  return res.data;
};

const eliminarPotencial = async (id) => {
  await api.delete(`${ENDPOINT_POTENCIALES}${id}/`);
};

const listarContactos = async (params = {}) => {
  const res = await api.get(ENDPOINT_CONTACTOS, { params });
  return res.data;
};

const detalleContacto = async (id) => {
  const res = await api.get(`${ENDPOINT_CONTACTOS}${id}/`);
  return res.data;
};

const crearContacto = async (data) => {
  const res = await api.post(ENDPOINT_CONTACTOS, data);
  return res.data;
};

const actualizarContacto = async (id, data) => {
  const res = await api.put(`${ENDPOINT_CONTACTOS}${id}/`, data);
  return res.data;
};

const actualizarContactoParcial = async (id, data) => {
  const res = await api.patch(`${ENDPOINT_CONTACTOS}${id}/`, data);
  return res.data;
};

const eliminarContacto = async (id) => {
  await api.delete(`${ENDPOINT_CONTACTOS}${id}/`);
};

const listarOportunidades = async (params = {}) => {
  const res = await api.get(ENDPOINT_OPORTUNIDADES, { params });
  return res.data;
};

const detalleOportunidad = async (id) => {
  const res = await api.get(`${ENDPOINT_OPORTUNIDADES}${id}/`);
  return res.data;
};

const crearOportunidad = async (data) => {
  const res = await api.post(ENDPOINT_OPORTUNIDADES, data);
  return res.data;
};

const actualizarOportunidad = async (id, data) => {
  const res = await api.put(`${ENDPOINT_OPORTUNIDADES}${id}/`, data);
  return res.data;
};

const actualizarOportunidadParcial = async (id, data) => {
  const res = await api.patch(`${ENDPOINT_OPORTUNIDADES}${id}/`, data);
  return res.data;
};

const eliminarOportunidad = async (id) => {
  await api.delete(`${ENDPOINT_OPORTUNIDADES}${id}/`);
};

const listarActividades = async (params = {}) => {
  const res = await api.get(ENDPOINT_ACTIVIDADES, { params });
  return res.data;
};

const detalleActividad = async (id) => {
  const res = await api.get(`${ENDPOINT_ACTIVIDADES}${id}/`);
  return res.data;
};

const crearActividad = async (data) => {
  const res = await api.post(ENDPOINT_ACTIVIDADES, data);
  return res.data;
};

const actualizarActividad = async (id, data) => {
  const res = await api.put(`${ENDPOINT_ACTIVIDADES}${id}/`, data);
  return res.data;
};

const actualizarActividadParcial = async (id, data) => {
  const res = await api.patch(`${ENDPOINT_ACTIVIDADES}${id}/`, data);
  return res.data;
};

const eliminarActividad = async (id) => {
  await api.delete(`${ENDPOINT_ACTIVIDADES}${id}/`);
};

export {
  listarPotenciales,
  detallePotencial,
  crearPotencial,
  actualizarPotencial,
  actualizarPotencialParcial,
  eliminarPotencial,
  listarContactos,
  detalleContacto,
  crearContacto,
  actualizarContacto,
  actualizarContactoParcial,
  eliminarContacto,
  listarOportunidades,
  detalleOportunidad,
  crearOportunidad,
  actualizarOportunidad,
  actualizarOportunidadParcial,
  eliminarOportunidad,
  listarActividades,
  detalleActividad,
  crearActividad,
  actualizarActividad,
  actualizarActividadParcial,
  eliminarActividad,
};