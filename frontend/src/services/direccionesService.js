// frontend/src/services/direccionesService.js
import api from "./api";

const BASE_URL = "/users/direcciones/";

/*** Obtiene TODAS las direcciones del usuario logueado.
 * (GET: /api/users/direcciones/) */
const listar = async () => {
    const res = await api.get(`${BASE_URL}`);
    return res.data;
};

/*** Crea una nueva dirección.
 * (POST: /api/users/direcciones/) */
const crear = async (datos) => {
    const res = await api.post(`${BASE_URL}`, datos);
    return res.data;
};

/*** Actualiza una dirección existente.
 * (PATCH: /api/users/direcciones/{id}/) */
const actualizar = async (id, datos) => {
    const res = await api.patch(`${BASE_URL}${id}/`, datos);
    return res.data;
};

/*** Obtiene el detalle de una dirección (si es necesario)
* (GET: /api/users/direcciones/{id}/) */
const detalle = async (id) => {
    const res = await api.get(`${BASE_URL}${id}/`);
    return res.data;
};

/*** Elimina una dirección.
 * (DELETE: /api/users/direcciones/{id}/) */
const eliminar = async (id) => {
    await api.delete(`${BASE_URL}${id}/`);
};

export default {
    listar,
    crear,
    actualizar,
    detalle,
    eliminar,
}