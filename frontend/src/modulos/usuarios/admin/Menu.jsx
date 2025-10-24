// src/components/Menu.jsx
import React from "react";
import { Menu, X } from "lucide-react";

export default function MobileSidebarToggle({ abierto, setAbierto }) {
  return (
    <button
      className="md:hidden p-2 rounded-md hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#2e7e8b]"
      onClick={() => setAbierto(v => !v)}
      aria-label={abierto ? "Cerrar menú" : "Abrir menú"}
      aria-expanded={abierto}
      aria-controls="sidebar-main"
      title={abierto ? "Cerrar menú" : "Abrir menú"}
    >
      {abierto ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
    </button>
  );
}
