import React from "react";
import { Link, Outlet } from "react-router-dom";

import { 
  ShoppingBag, Users, BarChart3, Shield, Smile, Rocket, Sparkles 
} from "lucide-react";

export default function Layout() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 antialiased flex">
      {/* Sidebar vertical */}
      <aside className="fixed top-0 left-0 h-screen w-64 bg-white shadow-lg z-50 flex flex-col items-center py-8 border-r border-slate-200">
        <div className="flex items-center gap-2 mb-10">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/30">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            ChanbaSoft
          </h1>
        </div>
        <nav className="w-full flex flex-col gap-4">
          <Link to="/register" className="w-full px-6 py-3 rounded-lg font-semibold text-slate-700 hover:bg-blue-50 hover:text-blue-700 transition flex items-center">
            <Users className="w-5 h-5 mr-3" /> Registro de Usuario
          </Link>
          <a href="#gestion-empleados" className="w-full px-6 py-3 rounded-lg font-semibold text-slate-700 hover:bg-blue-50 hover:text-blue-700 transition flex items-center">
            <Shield className="w-5 h-5 mr-3" /> Gestión de Empleados
          </a>
          <a href="#bitacora" className="w-full px-6 py-3 rounded-lg font-semibold text-slate-700 hover:bg-blue-50 hover:text-blue-700 transition flex items-center">
            <BarChart3 className="w-5 h-5 mr-3" /> Bitácora
          </a>
          <a href="#gestion-perfiles" className="w-full px-6 py-3 rounded-lg font-semibold text-slate-700 hover:bg-blue-50 hover:text-blue-700 transition flex items-center">
            <Smile className="w-5 h-5 mr-3" /> Gestión de Perfiles
          </a>
          <Link to="/productos" className="w-full px-6 py-3 rounded-lg font-semibold text-slate-700 hover:bg-blue-50 hover:text-blue-700 transition flex items-center">
            <ShoppingBag className="w-5 h-5 mr-3" /> Gestión de Productos
          </Link>
          <Link to="/carritos" className="w-full px-6 py-3 rounded-lg font-semibold text-slate-700 hover:bg-blue-50 hover:text-blue-700 transition flex items-center">
            <Rocket className="w-5 h-5 mr-3" /> Gestión de Carritos
          </Link>
        </nav>
      </aside>
      {/* Botón de login en la esquina superior derecha */}
      <div className="fixed top-6 right-8 z-50">
        <Link to="/login" className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2.5 rounded-full font-semibold shadow-lg hover:shadow-purple-500/40 transition-all duration-300 transform hover:scale-105">
          Login
        </Link>
      </div>
      {/* Main content, with left margin for sidebar */}
      <main className="flex-1 ml-64 pt-8">
        <Outlet />
      </main>
    </div>
  );
}
