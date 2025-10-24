// src/pages/DashAdmin.jsx
import React, { useState, useEffect, Suspense } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Search, Bell, HelpCircle, Settings, User,
  Users, UserCheck, FileText, Shield, Package, ShoppingCart,
  CreditCard, Handshake, BarChart2, Bot, ClipboardList, LogOut,
} from "lucide-react";
import toast from "react-hot-toast";

import logocrm from "../assets/logoCRM.png";
import MenuHorizontal from "../components/MenuHorizontal";
import MobileSidebarToggle from "../modulos/usuarios/admin/Menu";

import Productos from "../modulos/productos/GestionProductos";
import ProductosCategorias from "../modulos/productos/GestionCategoria";
import Almacenes from "../modulos/productos/almacenes/GestionAlmacenes";

import Empleados from "../modulos/empleados";
import GestionCarritos from "../modulos/carrito/GestionCarritos";
import Bitacora from "./Bitacora";
import UserProfile from "./UserProfile";

import api from "../services/api";
import { getRefreshToken, clearAuthTokens } from "../utils/auth";

import GestionUsuarios from "../modulos/usuarios/admin/GestionUsuarios";

const sidebarItems = [
  { name: "Usuarios", icon: <Users size={22} />, component: <GestionUsuarios /> },
  { name: "Empleados", icon: <UserCheck size={22} />, component: <Empleados /> },
  { name: "Bitácora", icon: <FileText size={22} />, component: <Bitacora /> },
  { name: "Perfiles", icon: <Shield size={22} />, component: <div>Contenido de Perfiles</div> },
  {
    name: "Productos", icon: <Package size={22} />, component: <Productos />,
    subMenu: [
      { name: "Listado", component: <Productos /> },
      { name: "Categorías", component: <ProductosCategorias /> },
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
  const [sidebarAbierto, setSidebarAbierto] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const firstSub = activeItem?.subMenu?.[0] ?? null;
    setActiveSubItem(firstSub);
    const container = document.querySelector("main[role='main']");
    if (container) container.scrollTop = 0;
    setSidebarAbierto(false);
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
        await api.post("/users/auth/logout/", { refresh });
      } else {
        console.warn("No se encontró refresh token en localStorage. Solo se limpiarán tokens locales.");
      }
    } catch (err) {
      console.warn("Error al llamar logout en backend:", err?.response?.data ?? err.message ?? err);
    } finally {
      clearAuthTokens();
      toast.success("Sesión cerrada correctamente.");
      navigate("/login");
    }
  };

  if (showProfile) return <UserProfile onBack={handleBackToDashboard} />;

  return (
    <div className="flex h-screen bg-gray-100 font-sans text-gray-800">
      <style>{`
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

      {/* ELIMINADO: El botón hamburguesa de aquí.
        Lo movimos DENTRO del <header> para un mejor flujo.
      */}

      {/* Overlay (sólo en móvil, cuando sidebar abierto) */}
      <div
        className={`fixed inset-0 z-30 bg-black/40 transition-opacity duration-200 md:hidden ${
          sidebarAbierto ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'
        }`}
        onClick={() => setSidebarAbierto(false)}
        aria-hidden={!sidebarAbierto}
      />

      {/* ASIDE: Sidebar responsive */}
      <aside
        id="sidebar-main"
        className={`
          fixed top-0 left-0 z-40 h-full w-64 bg-[#2e7e8b] text-white flex flex-col py-6 transform transition-transform duration-300
          md:static md:translate-x-0 md:w-56 md:flex md:flex-col
          ${sidebarAbierto ? 'translate-x-0' : '-translate-x-full'}
        `}
        aria-hidden={!sidebarAbierto && window?.innerWidth < 768}
        aria-label="Menú lateral principal"
      >
        {/* Logo */}
        <div className="flex items-center justify-between md:justify-start gap-3 px-4 mb-6">
          <Link to="/" className="flex items-center gap-3" onClick={() => setSidebarAbierto(false)}>
            <img src={logocrm} alt="Logo" className="w-10 h-10 sm:w-12 sm:h-12 md:w-14 md:h-14 object-contain" />
            {/* MEJORA: Eliminado 'hidden' para que 'MiApp' se vea en el menú móvil */}
            <span className="font-bold text-xl">MiApp</span>
          </Link>

          {/* Botón cerrar sólo visible mobile dentro del panel */}
          <div className="md:hidden pr-2">
            <button
              className="p-1 rounded-md hover:bg-white/10"
              onClick={() => setSidebarAbierto(false)}
              aria-label="Cerrar menú"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24"><path fill="currentColor" d="M18.3 5.71a1 1 0 0 0-1.41 0L12 10.59 7.11 5.7A1 1 0 0 0 5.7 7.11L10.59 12l-4.9 4.89a1 1 0 0 0 1.41 1.41L12 13.41l4.89 4.9a1 1 0 0 0 1.41-1.41L13.41 12l4.9-4.89a1 1 0 0 0 0-1.4z" /></svg>
            </button>
          </div>
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
                    {/* MEJORA: Eliminado 'hidden md:inline-block' para que el nombre se vea en móvil */}
                    <span>{item.name}</span>
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Logout */}
        <div className="border-t border-white/10 px-3 py-4">
          <button
            onClick={handleLogout}
            title="Cerrar Sesión"
            className="w-full flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[#2e7e8b] focus:ring-white text-gray-200 hover:bg-red-600 hover:text-white"
          >
            <LogOut size={22} />
            {/* MEJORA: Eliminado 'hidden md:inline-block' para que el texto se vea en móvil */}
            <span>Cerrar Sesión</span>
          </button>
        </div>
      </aside>

      {/* MAIN layout: header + submenu + contenido */}
      <div className="flex-1 flex flex-col overflow-hidden">
        
        {/* MEJORA: Header modificado para incluir el botón hamburguesa */}
        <header className="sticky top-0 z-20 w-full border-b bg-white shadow-sm px-4 sm:px-6 py-3">
          <div className="flex items-center justify-between gap-4">
            
            {/* Lado izquierdo: Botón (móvil) y Título */}
            <div className="flex items-center gap-3">
              {/* --- NUEVO --- */}
              {/* Botón hamburguesa (ahora dentro del header) */}
              <div className="md:hidden">
                <MobileSidebarToggle abierto={sidebarAbierto} setAbierto={setSidebarAbierto} />
              </div>
              {/* --- FIN NUEVO --- */}
              
              <h1 className="text-lg sm:text-xl font-semibold text-gray-800 line-clamp-1">{activeItem.name}</h1>
              
              {activeItem.subMenu?.length ? (
                // MEJORA: Oculto en pantallas extra pequeñas para no saturar
                <span className="ml-2 hidden sm:inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-800">
                  {activeItem.subMenu.length} secciones
                </span>
              ) : null}
            </div>

            {/* Lado derecho: Búsqueda e Iconos */}
            <div className="flex items-center gap-2 sm:gap-6">
              <div className="relative hidden lg:block">
                <input
                  type="text"
                  placeholder="Buscar en toda la app..."
                  className="w-full max-w-xs rounded-full border px-4 py-2 pl-10 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-[#2e7e8b]"
                />
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              </div>

              <div className="flex items-center space-x-2 sm:space-x-4 text-gray-600">
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
        <main role="main" className="p-4 sm:p-6 lg:p-8 flex-1 overflow-y-auto bg-gray-100">
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
        <footer className="bg-white border-t px-4 sm:px-6 py-3 text-sm text-slate-600">
          <div className="container mx-auto max-w-6xl">
            Sistema administrativo • {new Date().getFullYear()} • Hecho con Amor ❤️
          </div>
        </footer>
      </div>
    </div>
  );
}