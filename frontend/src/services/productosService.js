import api from "./api";

const ENDPOINT = "/productos/productos/";

// --- NUEVA FUNCIÓN AUXILIAR PARA SUBIR A CLOUDINARY ---
/**
 * Sube un archivo directamente a Cloudinary después de obtener una firma del backend.
 * @param {File} file - El archivo a subir.
 * @returns {Promise<string>} - La URL segura de la imagen subida.
 */
const uploadImageToCloudinary = async (file) => {
  // 1. Pedir la firma a nuestro backend
  const signResponse = await api.post('/productos/cloudinary/sign/', { 
    folder: 'boutique/productos' 
  });
  const signData = signResponse.data;

  // 2. Preparar el FormData para la API de Cloudinary
  const formData = new FormData();
  formData.append('file', file);
  formData.append('api_key', signData.api_key);
  formData.append('timestamp', signData.timestamp);
  formData.append('signature', signData.signature);
  formData.append('folder', signData.folder);

  // 3. Subir el archivo directamente a Cloudinary (usando fetch o axios sin interceptores)
  const cloudinaryUrl = `https://api.cloudinary.com/v1_1/${signData.cloud_name}/image/upload`;
  
  const cloudinaryResponse = await fetch(cloudinaryUrl, {
    method: 'POST',
    body: formData,
  });
  
  if (!cloudinaryResponse.ok) {
    throw new Error('Error al subir la imagen a Cloudinary');
  }

  const cloudinaryData = await cloudinaryResponse.json();
  
  // 4. Devolvemos la URL segura que nos da Cloudinary
  return cloudinaryData.secure_url;
};


// --- SERVICIOS PRINCIPALES (listar, detalle, eliminar no cambian) ---

const listar = async (params = {}) => {
  const res = await api.get(ENDPOINT, { params });
  return res.data;
};

const detalle = async (id) => {
  const res = await api.get(`${ENDPOINT}${id}/`);
  return res.data;
};

// --- FUNCIÓN 'crear' ADAPTADA ---
/**
 * Crea un nuevo producto.
 * @param {object} payload - El objeto con los datos del producto.
 * @param {object} payload.datos - Los datos del formulario (nombre, precio, etc.).
 * @param {File[]} payload.archivosDeImagenes - Un array de objetos File de las imágenes a subir.
 */
const crear = async ({ datos, archivosDeImagenes = [], almacenes_stock = [] }) => {
  // 1. Subir todas las imágenes a Cloudinary y obtener sus URLs
  const promesasDeSubida = archivosDeImagenes.map(file => uploadImageToCloudinary(file));
  const urlsDeImagenes = await Promise.all(promesasDeSubida);
  
  // 2. Construir el 'imagenes_payload' que espera el backend
  const imagenes_payload = urlsDeImagenes.map((url, index) => ({
    url: url,
    texto_alt: `Imagen de ${datos.nombre || 'producto'}`, // Texto alt por defecto
    es_principal: index === 0, // Marcar la primera imagen como principal
    orden: index,
  }));
  
  // 3. Enviar el payload final a nuestro backend
  const payloadFinal = { ...datos, imagenes_payload, almacenes_stock };
  const res = await api.post(ENDPOINT, payloadFinal);
  return res.data;
};

// --- FUNCIÓN 'actualizar' ADAPTADA ---
/**
 * Actualiza un producto existente.
 * @param {string|number} id - El ID del producto.
 * @param {object} payload - El objeto con los datos del producto.
 * @param {object} payload.datos - Los datos del formulario.
 * @param {File[]} [payload.nuevosArchivos] - Un array de nuevos archivos de imagen.
 * @param {object[]} [payload.imagenesExistentes] - Un array de las imágenes que se quieren conservar.
 */
const actualizar = async (id, { datos, nuevosArchivos = [], imagenesExistentes = [], almacenes_stock = [] }) => {
  // 1. Subir solo las imágenes nuevas
  const promesasDeSubida = nuevosArchivos.map(file => uploadImageToCloudinary(file));
  const urlsNuevas = await Promise.all(promesasDeSubida);

  // 2. Construir el payload de las imágenes nuevas
  const nuevasImagenesPayload = urlsNuevas.map((url, index) => ({
      url,
      texto_alt: `Imagen de ${datos.nombre || 'producto'}`,
      // Continuar el orden a partir de las existentes
      orden: imagenesExistentes.length + index, 
      es_principal: imagenesExistentes.length === 0 && index === 0, // Por defecto no son principal al añadir
  }));

  // 3. Unir las imágenes existentes con las nuevas y reordenar
  const imagenes_payload = [...imagenesExistentes, ...nuevasImagenesPayload].map((img, index) => ({
      ...img,
      orden: index, // Re-asignar el orden final
  }));
  
  // 4. Enviar el payload final
  const payloadFinal = { ...datos, imagenes_payload, almacenes_stock };
  const res = await api.put(`${ENDPOINT}${id}/`, payloadFinal);
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