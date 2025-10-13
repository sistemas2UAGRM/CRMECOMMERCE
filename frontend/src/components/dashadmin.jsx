import {
  Search, Bell, HelpCircle, Settings, User,
  Users, UserCheck, FileText, Shield, Package, ShoppingCart,
  CreditCard, Handshake, BarChart2, Bot, ClipboardList, LogOut,
} from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

import logocrm from "../assets/logoCRM.png";

import Productos from "../modulos/productos/producto";
import Empleados from "../modulos/empleados";
import GestionCarritos from "../modulos/carrito/GestionCarritos";
import Bitacora from "./Bitacora";
import UserProfile from "./UserProfile";
import { clearAuthTokens } from "../utils/auth";

import UsersAdminList from "../modulos/usuarios/admin/UsersAdminList";

const sidebarItems = [
  { name: "Usuarios", icon: <Users size={22} />, component: <UsersAdminList /> },
  { name: "Empleados", icon: <UserCheck size={22} />, component: <Empleados /> },
  { name: "Bitácora", icon: <FileText size={22} />, component: <Bitacora /> },
  { name: "Perfiles", icon: <Shield size={22} />, component: <div>Contenido de Perfiles</div> },
  { name: "Productos", icon: <Package size={22} />, component: <Productos /> },
  { name: "Carritos Activos", icon: <ShoppingCart size={22} />, component: <GestionCarritos /> },
  { name: "Pedidos", icon: <ClipboardList size={22} />, component: <div>Contenido de Pedidos</div> },
  { name: "Pagos", icon: <CreditCard size={22} />, component: <div>Contenido de Pagos</div> },
  { name: "CRM", icon: <Handshake size={22} />, component: <div>Contenido de CRM</div> },
  { name: "Reportes", icon: <BarChart2 size={22} />, component: <div>Contenido de Reportes</div> },
  { name: "IA", icon: <Bot size={22} />, component: <div>Contenido de IA</div> },
];

export default function DashAdmin() {
  // 3. El estado ahora puede guardar el objeto completo del item activo.
  // Empezamos con el primer item de la lista.
  const [activeItem, setActiveItem] = useState(sidebarItems[0]);
  const [showProfile, setShowProfile] = useState(false);
  const navigate = useNavigate();

  // Función para mostrar el perfil de usuario
  const handleShowProfile = () => {
    setShowProfile(true);
  };

  // Función para volver al dashboard
  const handleBackToDashboard = () => {
    setShowProfile(false);
  };

  // Función para cerrar sesión
  const handleLogout = () => {
    // Confirmar logout
    if (window.confirm('¿Estás seguro de que quieres cerrar sesión?')) {
      // Limpiar tokens y datos de autenticación
      clearAuthTokens();

      // Mostrar mensaje y redirigir
      alert('Sesión cerrada exitosamente');
      navigate('/login');
    }
  };

  // Si estamos mostrando el perfil, renderizamos solo el componente de perfil
  if (showProfile) {
    return <UserProfile onBack={handleBackToDashboard} />;
  }

  return (
    <div className="flex h-screen bg-gray-100 font-sans">
      {/* Sidebar */}
      <aside
        className="w-20 md:w-56 bg-[#2e7e8b] text-white flex flex-col items-center md:items-stretch py-6 shadow-lg transition-all duration-300"
        aria-label="Menú lateral"
      >
        {/* Logo en Sidebar */}
        <div className="flex items-center justify-center space-x-2 px-4 mb-8">
          <img src="/logo.png" alt="Logo" className="h-9 w-9" />
          <span className="hidden md:block font-bold text-xl text-white">MiApp</span>
        </div>

        <nav className="flex flex-col gap-4 px-2 flex-1">
          {sidebarItems.map((item) => (
            <button
              key={item.name}
              title={item.name} // Mejora de usabilidad para iconos solos
              className={`flex items-center justify-center md:justify-start gap-3 rounded-md px-3 py-2 text-sm font-medium transition focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[#2e7e8b] focus:ring-white ${activeItem.name === item.name
                ? "bg-[#f0a831] text-white"
                : "text-gray-200 hover:bg-white/20 hover:text-white"
                }`}
              onClick={() => setActiveItem(item)}
              aria-current={activeItem.name === item.name ? "page" : undefined}
            >
              {item.icon}
              <span className="hidden md:block">{item.name}</span>
            </button>
          ))}
        </nav>

        {/* Botón de Logout al final */}
        <div className="px-2 mt-auto">
          <button
            onClick={handleLogout}
            title="Cerrar Sesión"
            className="w-full flex items-center justify-center md:justify-start gap-3 rounded-md px-3 py-2 text-sm font-medium transition focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[#2e7e8b] focus:ring-white text-gray-200 hover:bg-red-600 hover:text-white border-t border-white/20 mt-4 pt-4"
          >
            <LogOut size={22} />
            <span className="hidden md:block">Cerrar Sesión</span>
          </button>
        </div>
      </aside>

      {/* Contenido principal */}
      <div className="flex-1 flex flex-col overflow-y-auto">
        {/* Header */}
        <header className="sticky top-0 z-10 w-full border-b bg-white shadow-sm px-6 py-3">
          <div className="flex items-center justify-between">
            {/* Título del Módulo Actual */}
            <h1 className="text-xl font-semibold text-gray-800">
              {activeItem.name}
            </h1>

            <div className="flex items-center gap-6">
              {/* Barra de búsqueda (opcional, puede estar dentro de cada módulo) */}
              <div className="relative hidden lg:block">
                <input
                  type="text"
                  placeholder="Buscar en toda la app..."
                  className="w-full max-w-xs rounded-full border px-4 py-2 pl-10 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-[#2e7e8b]"
                />
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              </div>

              {/* Iconos de usuario */}
              <div className="flex items-center space-x-5 text-gray-600">
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

        {/* Área de trabajo */}
        <main className="p-6 flex-1" role="main">
          {/* 4. Renderizado dinámico del componente activo */}
          {activeItem.component}
        </main>
      </div>
    </div>
  );
}
