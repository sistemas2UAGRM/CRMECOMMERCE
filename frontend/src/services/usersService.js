// frontend/src/services/usersService.js
import api from "./api";

const BASE_URL = "/users/users/"; 

/*** Obtiene la lista paginada de usuarios.
 * (GET: /api/users/users/)*/
const listar = async(params = {}) => {
  const res = await api.get(`${BASE_URL}`, { params });
  return res.data;
};

/*** Obtiene los detalles completos de un solo usuario.
 * (GET: /api/users/users/{id}/)*/
const detalle = async (id) => {
  const res = await api.get(`${BASE_URL}${id}/`);
  return res.data;
};

/*** (Admin) Crea un nuevo usuario desde el panel de admin.
 * (POST: /api/users/users/)*/
const crearPorAdmin = async (datos) => {
  const res = await api.post(`${BASE_URL}`, datos);
  return res.data;
};

/*** Actualiza los datos de un usuario.
 * (PATCH: /api/users/users/{id}/)*/
const actualizar = async (id, datos) => {
  const res = await api.patch(`${BASE_URL}${id}/`, datos);
  return res.data;
};

/**
 * Elimina un usuario.
 * (DELETE: /api/users/users/{id}/)
 */
const eliminar = async (id) => {
  await api.delete(`${BASE_URL}${id}/`);
};

/*** (Admin) Obtiene estadísticas de usuarios.
 * (GET: /api/users/users/stats/) */
const obtenerStats = async () => {
    const res = await api.get(`${BASE_URL}stats/`);
    return res.data;
}

/*** (Admin) Busca usuarios por query.
 * (GET: /api/users/users/search/?q=...) */
const buscar = async(query) => {
  const res = await api.get(`${BASE_URL}search/`, { params: { q: query } });
  return res.data;
}

// Exportamos solo el objeto default que usa nuestro Context
export default {
  listar,
  detalle,
  crearPorAdmin,
  actualizar,
  eliminar,
  obtenerStats,
  buscar,
};