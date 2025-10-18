// src/pages/DashAdmin.jsx
import React, { useState, useEffect, Suspense } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Search, Bell, HelpCircle, Settings, User,
  Users, UserCheck, FileText, Shield, Package, ShoppingCart,
  CreditCard, Handshake, BarChart2, Bot, ClipboardList, LogOut,
} from "lucide-react";

import logocrm from "../assets/logoCRM.png";
import MenuHorizontal from "../components/MenuHorizontal";

import Productos from "../modulos/productos/GestionProductos";
import ProductosCategorias from "../modulos/productos/GestionCategoria";
import Almacenes from "../modulos/productos/almacenes/GestionAlmacenes";

import Empleados from "../modulos/empleados";
import GestionCarritos from "../modulos/carrito/GestionCarritos";
import Bitacora from "./Bitacora";
import UserProfile from "./UserProfile";

import api from "../services/api"
import { getRefreshToken, clearAuthTokens } from "../utils/auth";

import UsersAdminList from "../modulos/usuarios/admin/UsersAdminList";

/* ------------------ Configuración del sidebar (tu original) ------------------ */
const sidebarItems = [
  { name: "Usuarios", icon: <Users size={22} />, component: <UsersAdminList /> },
  { name: "Empleados", icon: <UserCheck size={22} />, component: <Empleados /> },
  { name: "Bitácora", icon: <FileText size={22} />, component: <Bitacora /> },
  { name: "Perfiles", icon: <Shield size={22} />, component: <div>Contenido de Perfiles</div> },
  { name: "Productos", icon: <Package size={22} />, component: <Productos />,
    subMenu: [
      { name: "Listado", component: <Productos /> },
      { name: "Categorías", component: < ProductosCategorias /> },
      { name: "Almacenes", component: <Almacenes /> },
      { name: "Importar", component: <div>Importar productos (CSV)</div> },
    ],
  },
  { name: "Carritos Activos", icon: <ShoppingCart size={22} />, component: <GestionCarritos /> },
  { name: "Pedidos", icon: <ClipboardList size={22} />, component: <div>Contenido de Pedidos</div> },
  { name: "Pagos", icon: <CreditCard size={22} />, component: <div>Contenido de Pagos</div> },
  { name: "CRM", icon: <Handshake size={22} />, component: <div>Contenido de CRM</div> },
  { name: "Reportes", icon: <BarChart2 size={22} />, component: <div>Contenido de Reportes</div> },
  { name: "IA", icon: <Bot size={22} />, component: <div>Contenido de IA</div> },
];

/* ------------------ Loader simple (para Suspense) ------------------ */
function Loader() {
  return (
    <div className="flex items-center justify-center h-40">
      <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-[#2e7e8b]" />
      <span className="ml-3 text-sm text-slate-600">Cargando...</span>
    </div>
  );
}

/* ------------------ Componente principal ------------------ */
export default function DashAdmin() {
  const [activeItem, setActiveItem] = useState(sidebarItems[0]);
  const [activeSubItem, setActiveSubItem] = useState(null);
  const [showProfile, setShowProfile] = useState(false);
  const navigate = useNavigate();

  // Cuando cambia el módulo (activeItem), seleccionamos el primer subItem si existe
  useEffect(() => {
    const firstSub = activeItem?.subMenu?.[0] ?? null;
    setActiveSubItem(firstSub);
    // Scroll al top del contenido cuando cambiamos de módulo
    const container = document.querySelector("main[role='main']");
    if (container) container.scrollTop = 0;
  }, [activeItem]);

  // Mostrar perfil
  const handleShowProfile = () => setShowProfile(true);
  const handleBackToDashboard = () => setShowProfile(false);

  // Logout
  const handleLogout = async () => {
    if (!window.confirm("¿Estás seguro de que quieres cerrar sesión?")) return;
    const refresh = getRefreshToken();

    try {
      // Si tienes refresh, intenta avisar al backend para blacklistearlo
      if (refresh) {
        await api.post("/users/logout/", { refresh });
        // Si el access estaba expirado, el interceptor de api.js intentará refrescarlo y reintentar la petición.
      } else {
        console.warn("No se encontró refresh token en localStorage. Solo se limpiarán tokens locales.");
      }
    } catch (err) {
      // No detenemos el logout por errores en el backend: igual limpiamos cliente.
      // Ejemplos de fallos: refresh inválido, access expirado y refresh inválido, backend caído, etc.
      console.warn("Error al llamar logout en backend:", err?.response?.data ?? err.message ?? err);
    } finally {
      // Siempre limpiar tokens y redirigir
      clearAuthTokens();
      alert("Sesión cerrada exitosamente");
      navigate("/login");
    }
  };

  if (showProfile) return <UserProfile onBack={handleBackToDashboard} />;

  return (
    <div className="flex h-screen bg-gray-100 font-sans text-gray-800">
      {/* CSS local para scrollbar como respaldo (WebKit + Firefox) */}
      <style>{`
        /* clase .custom-scrollbar */
        .custom-scrollbar {
          scrollbar-width: thin;
          scrollbar-color: rgba(240,168,49,0.9) rgba(0,0,0,0.08);
        }
        .custom-scrollbar::-webkit-scrollbar { width: 10px; height: 10px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; border-radius: 9999px; }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background-color: rgba(240,168,49,0.9);
          border-radius: 9999px;
          border: 3px solid rgba(255,255,255,0.12);
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background-color: rgba(240,168,49,1); }
      `}</style>

      {/* ASIDE: Sidebar */}
      <aside
        className="w-20 md:w-56 bg-[#2e7e8b] text-white flex flex-col items-center md:items-stretch py-6 shadow-lg transition-all duration-300"
        aria-label="Menú lateral principal"
      >
        {/* Logo */}
        <div className="flex items-center justify-center md:justify-start gap-3 px-4 mb-6">
          <Link to="/" className="flex items-center gap-3">
            <img src={logocrm} alt="Logo" className="w-10 h-10 sm:w-12 sm:h-12 md:w-14 md:h-14 object-contain" />
            <span className="hidden md:inline-block font-bold text-xl">MiApp</span>
          </Link>
        </div>

        {/* Nav items - con scrollbar profesional */}
        <nav className="flex-1 w-full px-2 overflow-y-auto custom-scrollbar" aria-label="Navegación principal">
          <ul className="flex flex-col gap-2">
            {sidebarItems.map((item) => {
              const isActive = activeItem.name === item.name;
              return (
                <li key={item.name}>
                  <button
                    title={item.name}
                    onClick={() => setActiveItem(item)}
                    aria-current={isActive ? "page" : undefined}
                    className={`w-full flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors duration-200 transform ${
                      isActive
                        ? "bg-[#f0a831] text-white shadow-lg"
                        : "text-gray-200 hover:bg-white/10 hover:text-white"
                    }`}
                  >
                    <span className="flex items-center justify-center">{item.icon}</span>
                    <span className="hidden md:inline-block">{item.name}</span>
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Logout */}
        <div className="border-t border-gray-200 dark:border-gray-700 px-3 py-4">
          <button
            onClick={handleLogout}
            title="Cerrar Sesión"
            className="w-full flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[#2e7e8b] focus:ring-white text-gray-200 hover:bg-red-600 hover:text-white border-t border-white/10"
          >
            <LogOut size={22} />
            <span className="hidden md:inline-block">Cerrar Sesión</span>
          </button>
        </div>
      </aside>

      {/* MAIN layout: header + submenu + contenido */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="sticky top-0 z-10 w-full border-b bg-white shadow-sm px-6 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <h1 className="text-xl font-semibold text-gray-800">{activeItem.name}</h1>
              {/* Si tiene submenus mostramos un badge */}
              {activeItem.subMenu?.length ? (
                <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-800">
                  {activeItem.subMenu.length} secciones
                </span>
              ) : null}
            </div>

            <div className="flex items-center gap-6">
              <div className="relative hidden lg:block">
                <input
                  type="text"
                  placeholder="Buscar en toda la app..."
                  className="w-full max-w-xs rounded-full border px-4 py-2 pl-10 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-[#2e7e8b]"
                />
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              </div>

              <div className="flex items-center space-x-4 text-gray-600">
                <HelpCircle className="h-6 w-6 cursor-pointer hover:text-[#2e7e8b]" />
                <Settings className="h-6 w-6 cursor-pointer hover:text-[#2e7e8b]" />
                <Bell className="h-6 w-6 cursor-pointer hover:text-[#2e7e8b]" />
                <User
                  className="h-7 w-7 cursor-pointer hover:text-[#2e7e8b] transition-colors"
                  onClick={handleShowProfile}
                  title="Mi Perfil"
                />
              </div>
            </div>
          </div>
        </header>

        {/* Submenu horizontal integrado */}
        <section aria-label="Submenu del módulo" className="bg-white border-b">
          <MenuHorizontal
            items={activeItem.subMenu ?? []}
            activeSubItem={activeSubItem}
            onSubItemClick={(item) => setActiveSubItem(item)}
          />
        </section>

        {/* Área de contenido */}
        <main role="main" className="p-6 lg:p-8 flex-1 overflow-y-auto bg-gray-100">
          <Suspense fallback={<Loader />}>
            {/* Si hay subItem activo mostramos su componente, si no mostramos el componente del módulo */}
            {activeSubItem ? (
              activeSubItem.component ?? <div>Sin contenido para esta sección</div>
            ) : (
              activeItem.component ?? <div>Sin contenido para este módulo</div>
            )}
          </Suspense>
        </main>

        {/* Footer (opcional) */}
        <footer className="bg-white border-t px-6 py-3 text-sm text-slate-600">
          <div className="container mx-auto max-w-6xl">
            Sistema administrativo • {new Date().getFullYear()} • Hecho con Amor ❤️  
          </div>
        </footer>
      </div>
    </div>
  );
}
