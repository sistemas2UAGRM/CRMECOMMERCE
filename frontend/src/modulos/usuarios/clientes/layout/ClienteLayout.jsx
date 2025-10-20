import React, { useState } from 'react';
import { Link, Outlet, useNavigate } from 'react-router-dom';
import { Search, ShoppingCart, Bell, Package, User, Settings, LogOut } from 'lucide-react';
import { clearAuthTokens } from '../../../../utils/auth'; 

// --- Componente para el Dropdown del Perfil ---
const ProfileDropdown = ({ onLogout }) => {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <div className="relative">
            <button 
                onClick={() => setIsOpen(!isOpen)} 
                className="rounded-full w-10 h-10 bg-gray-200 flex items-center justify-center focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
                <User className="h-6 w-6 text-gray-600" />
            </button>

            {isOpen && (
                <div 
                    className="origin-top-right absolute right-0 mt-2 w-56 rounded-md shadow-lg py-1 bg-white ring-1 ring-black ring-opacity-5 z-20"
                    onMouseLeave={() => setIsOpen(false)} // Cierra el menú si el cursor sale
                >
                    <div className="px-4 py-3">
                        <p className="text-sm">Hola,</p>
                        <p className="text-sm font-medium text-gray-900 truncate">Edixon Apaza</p>
                    </div>
                    <div className="border-t border-gray-100"></div>
                    <Link to="/dashboard/perfil" className="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                        <User className="w-4 h-4" /> Mi Perfil
                    </Link>
                    <Link to="/dashboard/configuracion" className="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                        <Settings className="w-4 h-4" /> Configuración
                    </Link>
                    <div className="border-t border-gray-100"></div>
                    <button onClick={onLogout} className="flex w-full items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                        <LogOut className="w-4 h-4" /> Cerrar Sesión
                    </button>
                </div>
            )}
        </div>
    );
};

// --- Componente Principal del Layout ---
export default function ClienteLayout() {
    const navigate = useNavigate();

    const handleLogout = () => {
        // Aquí podrías llamar a tu endpoint /logout si lo tienes
        clearAuthTokens();
        navigate('/login');
    };
    
    return (
        <div className="min-h-screen bg-gray-100">
            {/* Header Superior Fijo */}
            <header className="bg-white shadow-sm sticky top-0 z-10">
                <div className="container mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16">
                        {/* Logo */}
                        <div className="flex-shrink-0">
                            <Link to="/dashboard" className="text-2xl font-bold text-indigo-600">
                                Boutique
                            </Link>
                        </div>

                        {/* Barra de Búsqueda (Centro) */}
                        <div className="hidden md:block flex-1 max-w-lg mx-4">
                            <div className="relative">
                                <span className="absolute inset-y-0 left-0 flex items-center pl-3">
                                    <Search className="h-5 w-5 text-gray-400" />
                                </span>
                                <input
                                    type="text"
                                    placeholder="Buscar productos, marcas y más..."
                                    className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-full leading-5 bg-gray-50 placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                                />
                            </div>
                        </div>

                        {/* Iconos y Perfil (Derecha) */}
                        <div className="flex items-center gap-5">
                            <Link to="/dashboard/pedidos" className="text-gray-500 hover:text-indigo-600" title="Mis Pedidos">
                                <Package className="h-6 w-6" />
                            </Link>
                            <Link to="/dashboard/notificaciones" className="text-gray-500 hover:text-indigo-600" title="Notificaciones">
                                <Bell className="h-6 w-6" />
                            </Link>
                            <Link to="/dashboard/carrito" className="relative text-gray-500 hover:text-indigo-600" title="Carrito de Compras">
                                <ShoppingCart className="h-6 w-6" />
                                {/* Badge de notificación del carrito */}
                                <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center border-2 border-white">3</span>
                            </Link>
                            <ProfileDropdown onLogout={handleLogout} />
                        </div>
                    </div>
                </div>
            </header>

            {/* Contenido Principal de la Página */}
            <main className="container mx-auto p-4 sm:p-6 lg:p-8">
                {/* Aquí se renderizará ProductList, UserProfile, etc. */}
                <Outlet />
            </main>
        </div>
    );
}