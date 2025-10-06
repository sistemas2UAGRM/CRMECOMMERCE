import axios from "axios";
import { getAuthToken } from "../utils/auth";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000/api/v1", // tu backend Django
});

// Interceptor para enviar token JWT en cada request
api.interceptors.request.use((config) => {
  // Endpoints públicos que no necesitan autenticación
  const publicEndpoints = ['/users/login/', '/users/register/'];
  const isPublicEndpoint = publicEndpoints.some(endpoint =>
    config.url?.includes(endpoint)
  );

  // Solo añadir token si no es un endpoint público
  if (!isPublicEndpoint) {
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }

  return config;
});

export default api;
