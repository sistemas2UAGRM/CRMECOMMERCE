// src/services/productosService.js
import api from "./api";

/*
  ENDPOINT: /productos/ (según tu router)
  Compatibilidad:
  - Para crear/actualizar con imágenes y categorias usamos FormData con:
    - campos simples (nombre, precio, ...)
    - categoria_ids (varios valores)
    - imagenes[i].imagen, imagenes[i].texto_alt, imagenes[i].es_principal, imagenes[i].orden
*/

const ENDPOINT = "/productos/productos/";

const listar = async (params = {}) => {
  const res = await api.get(ENDPOINT, { params });
  return res.data;
};

const detalle = async (id) => {
  const res = await api.get(`${ENDPOINT}${id}/`);
  return res.data;
};

// Helper: convierte objeto + array de imagenes a FormData compatible con DRF
function buildProductoFormData(datos, imagenes = []) {
  const fd = new FormData();

  // Campos simples
  Object.entries(datos).forEach(([k, v]) => {
    if (v === undefined || v === null) return;
    // Si es array y no es categoria_ids (ej. tags) envía como JSON string
    if (Array.isArray(v) && k !== "categoria_ids") {
      fd.append(k, JSON.stringify(v));
    } else {
      fd.append(k, v);
    }
  });

  // categorias -> enviar como categoria_ids (varios valores)
  if (datos.categoria_ids && Array.isArray(datos.categoria_ids)) {
    datos.categoria_ids.forEach(id => {
      // DRF acepta varias entradas con mismo nombre
      fd.append("categoria_ids", id);
    });
  }

  // Imagenes: esperar array de objetos { file, texto_alt, es_principal, orden }
  imagenes.forEach((img, i) => {
    // file es obligatorio para subir archivo
    if (img.file) {
      fd.append(`imagenes[${i}].imagen`, img.file);
    }
    if (img.texto_alt !== undefined) fd.append(`imagenes[${i}].texto_alt`, img.texto_alt);
    if (img.es_principal !== undefined) fd.append(`imagenes[${i}].es_principal`, img.es_principal ? "true" : "false");
    if (img.orden !== undefined) fd.append(`imagenes[${i}].orden`, img.orden);
  });

  return fd;
}

const crear = async ({ datos, imagenes = [] }) => {
  // espera { datos: { nombre,..., categoria_ids: [1,2] }, imagenes: [{file, texto_alt,...}, ...] }
  const fd = buildProductoFormData(datos, imagenes);
  const res = await api.post(ENDPOINT, fd, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
};

const actualizar = async (id, { datos, imagenes = [] }) => {
  const fd = buildProductoFormData(datos, imagenes);
  const res = await api.put(`${ENDPOINT}${id}/`, fd, {
    headers: { "Content-Type": "multipart/form-data" },
  });
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
