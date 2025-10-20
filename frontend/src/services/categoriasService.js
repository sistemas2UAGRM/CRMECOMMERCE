// src/services/categoriasService.js
import api from "./api";

const ENDPOINT = "/ecommerce/categorias/";

const listar = async () => {
  const res = await api.get(ENDPOINT);
  return res.data;
};

const detalle = async (id) => {
  const res = await api.get(`${ENDPOINT}${id}/`);
  return res.data;
};

const crear = async (datos) => {
  const res = await api.post(ENDPOINT, datos);
  return res.data;
};

const actualizar = async (id, datos) => {
  const res = await api.put(`${ENDPOINT}${id}/`, datos);
  return res.data;
};

const eliminar = async (id) => {
  const res = await api.delete(`${ENDPOINT}${id}/`);
  return res.data;
};

export default {
  listar,
  detalle,
  crear,
  actualizar,
  eliminar,
};
