import axios from "axios";
import { getAuthToken, getRefreshToken, setAuthTokens, clearAuthTokens } from '../utils/auth';

const api = axios.create({
  //baseURL: "http://127.0.0.1:8000/api/v1", // tu backend Django
  baseURL: "http://127.0.0.1:8000/api",
  headers: {
    'Content-Type': 'application/json',
  },
});

const PUBLIC_PATHS = ['/login/', '/register/', '/token/refresh/', '/token/verify/'];

// Request interceptor: añade Authorization si corresponde
api.interceptors.request.use((config) => {
  const url = config.url || '';
  const isPublic = PUBLIC_PATHS.some(p => url.endsWith(p) || url.includes(p));
  if (!isPublic) {
    const token = getAuthToken();
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => Promise.reject(error));

// --- Refresh token logic (cola para peticiones concurrentes) ---
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) prom.reject(error);
    else prom.resolve(token);
  });
  failedQueue = [];
};

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (!originalRequest) return Promise.reject(error);

    const status = error.response?.status;

    // Si 401 y la petición no fue el endpoint de refresh
    if (status === 401 && !originalRequest._retry && !(originalRequest.url?.includes('/token/refresh/'))) {
      const refresh = getRefreshToken();
      if (!refresh) {
        // no hay refresh -> forzar logout
        clearAuthTokens();
        // redirigir a login (usa router si lo prefieres)
        window.location.href = '/login';
        return Promise.reject(error);
      }

      if (isRefreshing) {
        // estamos refrescando: devolver promesa que se resolverá cuando termine
        return new Promise(function (resolve, reject) {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          originalRequest.headers['Authorization'] = 'Bearer ' + token;
          return api(originalRequest);
        }).catch(err => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        // Llamada directa al endpoint de refresh (no usar la instancia api para evitar loop)
        const resp = await axios.post(`${'http://127.0.0.1:8000/api'}/token/refresh/`, { refresh });
        const newAccess = resp.data.access;
        const newRefresh = resp.data.refresh ?? refresh; // si rota refresh tokens, actualízalo

        // Guardar tokens nuevos
        setAuthTokens({ access: newAccess, refresh: newRefresh });

        // Actualizar cabecera default y la cabecera original
        api.defaults.headers.common['Authorization'] = 'Bearer ' + newAccess;
        originalRequest.headers['Authorization'] = 'Bearer ' + newAccess;

        processQueue(null, newAccess);
        return api(originalRequest);
      } catch (err) {
        processQueue(err, null);
        clearAuthTokens();
        window.location.href = '/login';
        return Promise.reject(err);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default api;