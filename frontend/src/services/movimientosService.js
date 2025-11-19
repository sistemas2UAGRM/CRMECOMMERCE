// frontend/src/services/movimientosService.js
import api from "./api";
const ENDPOINT = "/productos/movimientos-stock/";

const listar = async (params = {}) => {
  const res = await api.get(ENDPOINT, { params });
  return res.data;
};

const crear = async (datos) => {
  const res = await api.post(ENDPOINT, datos);
  return res.data;
};

export default { listar, crear };
