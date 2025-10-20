// components/Header.jsx
import React from 'react';
import { Menu, Search, Bell } from 'lucide-react';
import { Link } from 'react-router-dom';

/**
 * Props:
 * - toggleSidebar: función para abrir/cerrar sidebar
 * - sidebarOpen (opcional): boolean para aria-expanded
 */
export default function Header({ toggleSidebar, sidebarOpen = false }) {
  return (
    <header className="bg-white shadow-md p-4 flex items-center justify-between sticky top-0 z-20">
      {/* Left: botón de menú móvil + brand */}
      <div className="flex items-center gap-3">
        {/* Botón hamburguesa móvil */}
        <button
          onClick={toggleSidebar}
          className="p-2 rounded-md md:hidden hover:bg-gray-100"
          aria-label="Abrir menú de navegación"
          aria-controls="sidebar"              /* opcional: id del sidebar */
          aria-expanded={!!sidebarOpen}
        >
          <Menu size={22} />
        </button>

        {/* Logo/brand -> enlace al inicio */}
        <Link to="/" className="flex items-center gap-3" aria-label="Ir al inicio">
          <img src="/logo.svg" alt="Logo de Mi Tienda" className="w-8 h-8 rounded" />
          <span className="font-semibold text-gray-800">Mi Tienda</span>
        </Link>
      </div>

      {/* Centro: búsqueda (form semántico) */}
      <div className="flex-1 px-4">
        <form
          role="search"
          className="relative max-w-md mx-auto hidden sm:block"
          onSubmit={(e) => {
            e.preventDefault();
            // aquí podrías manejar la búsqueda o delegarla a props
          }}
        >
          {/* label accesible */}
          <label htmlFor="search-input" className="sr-only">
            Buscar productos
          </label>

          <input
            id="search-input"
            name="q"
            aria-label="Buscar productos"
            type="search"
            placeholder="Buscar..."
            className="w-full pl-10 pr-4 py-2 border rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500"
          />

          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} aria-hidden="true" />
        </form>
      </div>

      {/* Right: acciones */}
      <div className="flex items-center gap-3">
        <button
          aria-label="Ver notificaciones"
          className="p-2 rounded hover:bg-gray-100"
          title="Notificaciones"
        >
          <Bell size={20} />
        </button>

        <Link to="/profile" className="flex items-center gap-2" aria-label="Ir al perfil">
          <img
            src="https://randomuser.me/api/portraits/men/32.jpg"
            alt="Foto de perfil de usuario"
            className="w-9 h-9 rounded-full"
          />
        </Link>
      </div>
    </header>
  );
}
