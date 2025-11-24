// frontend/src/utils/auth.js
const TOKEN_KEY = 'token';
const REFRESH_KEY = 'refreshToken';
const LEGACY_ACCESS = 'accessToken';

export const getAuthToken = () => {
  let token = localStorage.getItem(TOKEN_KEY);
  if (!token) {
    const old = localStorage.getItem(LEGACY_ACCESS);
    if (old) {
      localStorage.setItem(TOKEN_KEY, old);
      localStorage.removeItem(LEGACY_ACCESS);
      token = old;
      console.debug('Token migrado de accessToken a token');
    }
  }
  return token;
};

export const getRefreshToken = () => {
  return localStorage.getItem(REFRESH_KEY);
};

export const setAuthTokens = ({ access = null, refresh = null }) => {
  if (access) localStorage.setItem(TOKEN_KEY, access);
  if (refresh) localStorage.setItem(REFRESH_KEY, refresh);

  // limpiar nombres viejos por si quedaron
  localStorage.removeItem(LEGACY_ACCESS);
};

export const clearAuthTokens = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
  localStorage.removeItem(LEGACY_ACCESS);
  localStorage.removeItem('user');
};

export const setUser = (userObj) => {
  if (userObj) localStorage.setItem('user', JSON.stringify(userObj));
};

export const getUser = () => {
  const s = localStorage.getItem('user');
  return s ? JSON.parse(s) : null;
};

export const isTokenExpiredError = (error) => {
  // utilidad simple para detectar error 401 por expiración
  if (!error || !error.response) return false;
  const status = error.response.status;
  if (status === 401) return true;
  return false;
};