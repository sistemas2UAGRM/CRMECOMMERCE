import axios from "axios";
import { getAuthToken } from "../utils/auth";

const api = axios.create({
  baseURL: "http://localhost:8000/api/v1", // tu backend Django
});

// Interceptor para enviar token JWT en cada request
api.interceptors.request.use((config) => {
  const token = getAuthToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  } else {
    delete config.headers.Authorization; // evita 'Bearer undefined'
  }
  return config;
});

export default api;
