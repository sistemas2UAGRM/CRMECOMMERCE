// src/services/authService.js (NUEVO)
import api from './api';
import { setAuthTokens, clearAuthTokens, setUser } from '../utils/auth';

/*** Inicia sesión de usuario.
 * (POST: /api/users/auth/login/) */
const login = async (email, password) => {
    const response = await api.post("/users/auth/login/", { email, password });
    const { access_token, refresh_token, user } = response.data;

    if (access_token) {
        setAuthTokens({ access: access_token, refresh: refresh_token });
        if (user) setUser(user);
    }
    return response.data;
};

/*** Registra un nuevo usuario público.
 * (POST: /api/users/auth/signup/) */
const signup = async (userData) => {
    const response = await api.post("/users/auth/signup/", userData);
    return response.data;
};

/*** Cierra la sesión (invalida el refresh token).
 * (POST: /api/users/auth/logout/) */
const logout = async (refresh) => {
    try {
        if (refresh) {
            await api.post("/users/auth/logout/", { refresh });
        }
    } finally {
        clearAuthTokens();
    }
};

/*** Obtiene el perfil del usuario autenticado.
 * (GET: /api/users/users/profile/) */
const getProfile = async () => {
    const response = await api.get("/users/users/profile/");
    return response.data;
};

/*** Actualiza el perfil del usuario autenticado.
 * (PATCH: /api/users/users/profile/) */
const updateProfile = async (datos) => {
    const response = await api.patch("/users/users/profile/", datos);
    return response.data;
};

export default {
    login,
    signup,
    logout,
    getProfile,
    updateProfile,
};