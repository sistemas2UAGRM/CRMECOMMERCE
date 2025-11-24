// frontend/src/services/api.js
import axios from "axios";
import { getAuthToken, getRefreshToken, setAuthTokens, clearAuthTokens } from '../utils/auth';

// --- LÓGICA MULTI-TENANT ---
const getBaseUrl = () => {
  const { protocol, hostname } = window.location;

  if (hostname.includes('localhost') || hostname === '127.0.0.1') {
    return `${protocol}//${hostname}:8000/api`;
  }

  // Configuración para producción (asumiendo que backend y frontend comparten dominio base o usan proxy)
  // Opción A: Backend en api.tienda1.dominio.com
  // Opción B: Backend en tienda1.backend.com
  // Opción C (Recomendada): tienda1.dominio.com/api (Proxy inverso con Nginx)
  return `${protocol}//${hostname}:8000/api`;
};

const api = axios.create({
  baseURL: getBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
});

const PUBLIC_PATHS = [
  '/users/auth/login/',
  '/users/auth/signup/',
  '/users/auth/verify/',
  '/users/auth/resend-verification/',
  '/users/token/refresh/',
  '/users/token/verify/',
];

// Request interceptor: añade Authorization si corresponde
api.interceptors.request.use((config) => {
  const url = config.url || '';
  const isPublic = PUBLIC_PATHS.some(p => url === p || url.startsWith(p));
  if (!isPublic) {
    const token = getAuthToken();
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => Promise.reject(error));

// --- Lógica de Refresh token ---
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
    const url = originalRequest.url || '';

    // Si 401 y la petición no fue el endpoint de refresh
    if (status === 401 && !originalRequest._retry && !PUBLIC_PATHS.some(p => url === p)) {
      const refresh = getRefreshToken();
      if (!refresh) {
        clearAuthTokens();
        window.location.href = '/login';
        return Promise.reject(error);
      }

      if (isRefreshing) {
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
        //const resp = await axios.post(`${'http://127.0.0.1:8000/api'}/users/token/refresh/`, { refresh });
        const resp = await axios.post(`${api.defaults.baseURL}/users/token/refresh/`, { refresh });
        const newAccess = resp.data.access;
        const newRefresh = resp.data.refresh ?? refresh;

        // Guardar tokens nuevos
        setAuthTokens({ access: newAccess, refresh: newRefresh });
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