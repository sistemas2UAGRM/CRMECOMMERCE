// src/services/usersService.js (VERSIÓN CORREGIDA Y LIMPIA)
import api from "./api";

// Esta URL base es CORRECTA según tu apps/users/urls.py
const BASE = "/users/users/"; 

// Esta URL para crear es CORRECTA según tu apps/users/urls.py
const CREAR_ADMIN_URL = "/users/auth/signup/";

/**
 * Obtiene la lista paginada de usuarios.
 * (GET: /api/users/users/)
 */
const listar = async (params = {}) => {
  const res = await api.get(`${BASE}`, { params });
  return res.data;
};

/**
 * Obtiene los detalles completos de un solo usuario.
 * (GET: /api/users/users/{id}/)
 */
const detalle = async (id) => {
  const res = await api.get(`${BASE}${id}/`);
  return res.data;
};

export const adminCreateUser = (payload) => api.post(BASE, payload);
/**
 * Crea un nuevo usuario desde el panel de administración.
 * (POST: /api/users/admin-register/)
 */
const crearPorAdmin = async (datos) => {
  const res = await api.post(CREAR_ADMIN_URL, datos);
  return res.data;
};

/**
 * Actualiza los datos de un usuario.
 * (PATCH: /api/users/users/{id}/)
 */
const actualizar = async (id, datos) => {
  const res = await api.patch(`${BASE}${id}/`, datos);
  return res.data;
};

/**
 * Elimina un usuario.
 * (DELETE: /api/users/users/{id}/)
 */
const eliminar = async (id) => {
  await api.delete(`${BASE}${id}/`);
};

/**
 * Obtiene estadísticas de usuarios.
 * (GET: /api/users/stats/ - Asumiendo que está en /api/users/stats/)
 */
const obtenerStats = async () => {
    const res = await api.get("/users/stats/");
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
};