import React, { createContext, useState, useContext, useEffect } from 'react';
import api from '../services/api';

const ThemeContext = createContext();

export const useTheme = () => useContext(ThemeContext);

export const ThemeProvider = ({ children }) => {
    const [theme, setTheme] = useState({
        color: '#3B82F6', // Default blue
        fontSize: 'medium', // small, medium, large
    });

    const [isLoaded, setIsLoaded] = useState(false);

    const userHasChangedTheme = React.useRef(false);

    // Cargar preferencias del usuario al iniciar
    useEffect(() => {
        const loadPreferences = async () => {
            try {
                const response = await api.get('/users/users/profile/');
                const prefs = response.data.profile?.preferencias_ui;
                if (prefs) {
                    setTheme(prev => ({ ...prev, ...prefs }));
                }
            } catch (error) {
                console.error('Error loading theme preferences:', error);
            } finally {
                setIsLoaded(true);
            }
        };
        loadPreferences();
    }, []);

    // Aplicar estilos al body/root
    useEffect(() => {
        document.documentElement.style.setProperty('--primary-color', theme.color);

        const fontSizes = {
            small: '14px',
            medium: '16px',
            large: '18px'
        };
        document.documentElement.style.setProperty('--base-font-size', fontSizes[theme.fontSize] || '16px');
        document.body.style.fontSize = fontSizes[theme.fontSize] || '16px';

    }, [theme]);

    // Persistir cambios en el backend con debounce
    useEffect(() => {
        if (!isLoaded || !userHasChangedTheme.current) return;

        const timeoutId = setTimeout(async () => {
            try {
                await api.patch('/users/users/profile/', {
                    profile: {
                        preferencias_ui: theme
                    }
                });
            } catch (error) {
                console.error('Error saving theme preferences:', error);
            }
        }, 1000);

        return () => clearTimeout(timeoutId);
    }, [theme, isLoaded]);

    const updateTheme = (newTheme) => {
        userHasChangedTheme.current = true;
        setTheme(prev => ({ ...prev, ...newTheme }));
    };

    return (
        <ThemeContext.Provider value={{ theme, updateTheme }}>
            {children}
        </ThemeContext.Provider>
    );
};
