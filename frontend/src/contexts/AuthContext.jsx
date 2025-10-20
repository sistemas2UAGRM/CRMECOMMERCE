// src/contexts/AuthContext.jsx (NUEVO)
import React, { createContext, useState, useContext, useEffect } from 'react';
import { getUser as getLocalUser, getAuthToken, clearAuthTokens } from '../utils/auth';
import authService from '../services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUserState] = useState(getLocalUser());
    const [isAuthenticated, setIsAuthenticated] = useState(!!getAuthToken());

    const login = async (email, password) => {
        const data = await authService.login(email, password);
        setUserState(data.user);
        setIsAuthenticated(true);
        return data.user;
    };

    const logout = () => {
        authService.logout(localStorage.getItem('refreshToken'));
        setUserState(null);
        setIsAuthenticated(false);
    };

    const value = { user, isAuthenticated, login, logout };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth debe ser usado dentro de un AuthProvider');
    }
    return context;
};