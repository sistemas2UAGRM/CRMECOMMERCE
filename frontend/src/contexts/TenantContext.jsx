// frontend/src/contexts/TenantContext.jsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const TenantContext = createContext();

// Configura aquí tu dominio principal (sin subdominios)
const MAIN_DOMAIN = '127.0.0.1'; // Cambiar a 'tudominio.com' en producción

export const TenantProvider = ({ children }) => {
    const [tenant, setTenant] = useState(null);
    const [isMainDomain, setIsMainDomain] = useState(false);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const checkTenant = async () => {
            const hostname = window.location.hostname;

            // 1. Verificar si estamos en el dominio principal (Landing Page)
            if (hostname === MAIN_DOMAIN || hostname === `www.${MAIN_DOMAIN}`) {
                setIsMainDomain(true);
                setLoading(false);
                return;
            }

            // 2. Si es un subdominio, verificamos con el backend si existe
            try {
                const response = await api.get('/tenant-info/');
                if (response.data.type === 'public') {
                    // El backend dice que es esquema público (por si acaso)
                    setIsMainDomain(true);
                } else {
                    // Es un tenant válido
                    setTenant(response.data.data);
                }
            } catch (err) {
                console.error("Error verificando tenant:", err);
                setError("No pudimos encontrar esta tienda.");
            } finally {
                setLoading(false);
            }
        };

        checkTenant();
    }, []);

    // Pantalla de carga inicial mientras resolvemos dónde estamos
    if (loading) {
        return <div className="h-screen flex items-center justify-center">Cargando tienda...</div>;
    }

    // Pantalla de error si el subdominio no existe en backend
    if (error && !isMainDomain) {
        return (
            <div className="h-screen flex flex-col items-center justify-center bg-gray-50">
                <h1 className="text-4xl font-bold text-gray-800 mb-4">404</h1>
                <p className="text-xl text-gray-600">{error}</p>
                <a href={`http://${MAIN_DOMAIN}:4000`} className="mt-6 text-blue-600 hover:underline">
                    Ir al sitio principal
                </a>
            </div>
        );
    }

    return (
        <TenantContext.Provider value={{ tenant, isMainDomain }}>
            {children}
        </TenantContext.Provider>
    );
};

export const useTenant = () => useContext(TenantContext);