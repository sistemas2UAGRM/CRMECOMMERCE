import axios from "axios";
import { getAuthToken } from "../utils/auth";

const api = axios.create({
<<<<<<< HEAD
  //baseURL: "http://127.0.0.1:8000/api/v1", // tu backend Django
  baseURL: "http://127.0.0.1:8000/api",
=======
  baseURL: "http://localhost:8000/api/v1", // tu backend Django
>>>>>>> fc24bea7b9446d7af14c81c6b367159d845d8b56
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
