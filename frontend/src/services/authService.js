// src/services/authService.js (NUEVO)
import api from './api';
import { setAuthTokens, clearAuthTokens, setUser } from '../utils/auth';

const login = async (email, password) => {
    const response = await api.post("/users/login/", { email, password });
    const { access_token, refresh_token, user } = response.data;

    if (access_token) {
        setAuthTokens({ access: access_token, refresh: refresh_token });
        if (user) setUser(user);
    }
    return response.data;
};

const register = (userData) => {
    return api.post("/users/register/", userData);
};

const logout = async (refresh) => {
    try {
        if (refresh) {
            await api.post("/users/logout/", { refresh });
        }
    } finally {
        // Siempre limpiar tokens del cliente, incluso si el backend falla
        clearAuthTokens();
    }
};

export default {
    login,
    register,
    logout,
};