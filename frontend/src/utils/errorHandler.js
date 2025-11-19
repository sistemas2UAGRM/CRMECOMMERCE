/**
 * Extrae mensajes de error detallados de las respuestas de la API de Django REST Framework
 * @param {Error} error - El objeto de error capturado
 * @param {string} defaultMessage - Mensaje por defecto si no se puede extraer uno específico
 * @returns {string} - Mensaje de error formateado
 */
export const extractErrorMessage = (error, defaultMessage = 'Ha ocurrido un error') => {
  // Si no hay respuesta del servidor
  if (!error.response) {
    if (error.message === 'Network Error') {
      return 'Error de conexión. Verifica tu conexión a internet.';
    }
    return error.message || defaultMessage;
  }

  const { data, status } = error.response;

  // Errores de autenticación
  if (status === 401) {
    return 'Sesión expirada. Por favor, inicia sesión nuevamente.';
  }

  // Errores de permisos
  if (status === 403) {
    return 'No tienes permisos para realizar esta acción.';
  }

  // Errores de recurso no encontrado
  if (status === 404) {
    return 'Recurso no encontrado.';
  }

  // Si hay un mensaje de error directo (detail)
  if (data?.detail) {
    return Array.isArray(data.detail) ? data.detail.join(', ') : data.detail;
  }

  // Si hay errores de validación de campos
  if (data && typeof data === 'object') {
    const fieldErrors = [];
    
    for (const [field, errors] of Object.entries(data)) {
      if (Array.isArray(errors)) {
        const fieldName = field === 'non_field_errors' ? '' : `${field}: `;
        fieldErrors.push(`${fieldName}${errors.join(', ')}`);
      } else if (typeof errors === 'string') {
        const fieldName = field === 'non_field_errors' ? '' : `${field}: `;
        fieldErrors.push(`${fieldName}${errors}`);
      } else if (typeof errors === 'object') {
        // Errores anidados
        const nestedErrors = Object.values(errors).flat();
        fieldErrors.push(`${field}: ${nestedErrors.join(', ')}`);
      }
    }
    
    if (fieldErrors.length > 0) {
      return fieldErrors.join(' | ');
    }
  }

  // Mensaje por defecto
  return defaultMessage;
};

/**
 * Wrapper para manejar errores en llamadas API con toast
 * @param {Function} apiCall - Función asíncrona que realiza la llamada API
 * @param {Function} toast - Función toast para mostrar mensajes
 * @param {string} successMessage - Mensaje de éxito (opcional)
 * @param {string} errorMessage - Mensaje de error por defecto
 * @returns {Promise} - Resultado de la llamada API o null en caso de error
 */
export const handleApiCall = async (apiCall, toast, successMessage = null, errorMessage = 'Error en la operación') => {
  try {
    const result = await apiCall();
    if (successMessage) {
      toast.success(successMessage);
    }
    return result;
  } catch (error) {
    const message = extractErrorMessage(error, errorMessage);
    toast.error(message);
    console.error('API Error:', error.response?.data || error);
    return null;
  }
};

/**
 * Valida un formulario antes de enviar
 * @param {Object} formData - Datos del formulario
 * @param {Object} rules - Reglas de validación { campo: { required: true, minLength: 3, ... } }
 * @returns {Object} - { isValid: boolean, errors: { campo: string } }
 */
export const validateForm = (formData, rules) => {
  const errors = {};
  
  for (const [field, fieldRules] of Object.entries(rules)) {
    const value = formData[field];
    
    // Validación de requerido
    if (fieldRules.required && (!value || (typeof value === 'string' && value.trim() === ''))) {
      errors[field] = `${fieldRules.label || field} es requerido`;
      continue;
    }
    
    // Si no es requerido y está vacío, skip otras validaciones
    if (!value && !fieldRules.required) continue;
    
    // Validación de longitud mínima
    if (fieldRules.minLength && value.length < fieldRules.minLength) {
      errors[field] = `${fieldRules.label || field} debe tener al menos ${fieldRules.minLength} caracteres`;
    }
    
    // Validación de longitud máxima
    if (fieldRules.maxLength && value.length > fieldRules.maxLength) {
      errors[field] = `${fieldRules.label || field} no puede exceder ${fieldRules.maxLength} caracteres`;
    }
    
    // Validación de email
    if (fieldRules.email && value) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(value)) {
        errors[field] = `${fieldRules.label || field} debe ser un email válido`;
      }
    }
    
    // Validación de número
    if (fieldRules.number && value && isNaN(Number(value))) {
      errors[field] = `${fieldRules.label || field} debe ser un número`;
    }
    
    // Validación personalizada
    if (fieldRules.custom && typeof fieldRules.custom === 'function') {
      const customError = fieldRules.custom(value, formData);
      if (customError) {
        errors[field] = customError;
      }
    }
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

/**
 * Formatea una fecha de ISO a formato local datetime-local input
 * @param {string} isoDate - Fecha en formato ISO
 * @returns {string} - Fecha en formato YYYY-MM-DDTHH:MM
 */
export const formatDateForInput = (isoDate) => {
  if (!isoDate) return '';
  const date = new Date(isoDate);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${year}-${month}-${day}T${hours}:${minutes}`;
};

/**
 * Formatea una fecha para mostrar en UI
 * @param {string} dateString - Fecha en formato ISO o string
 * @param {boolean} includeTime - Si incluir la hora
 * @returns {string} - Fecha formateada
 */
export const formatDateForDisplay = (dateString, includeTime = false) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  const options = {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    ...(includeTime && { hour: '2-digit', minute: '2-digit' })
  };
  return date.toLocaleDateString('es-ES', options);
};
