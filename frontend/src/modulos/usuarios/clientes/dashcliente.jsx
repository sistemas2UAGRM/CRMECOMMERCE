// DashCliente.jsx
import React, { useState } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Profile from './components/Profile';
import Ordenes from './components/Ordenes';
import Carrito from './components/Carrito';
import Configuraciones from './components/Configuraciones';
import ProductList from './ProductoLista';

export default function DashCliente() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const openSidebar = () => setSidebarOpen(true);
  const closeSidebar = () => setSidebarOpen(false);
  const toggleSidebar = () => setSidebarOpen(prev => !prev);

  return (
    <div className="flex bg-gray-100 min-h-screen">
      {/* Sidebar recibe un id para que Header pueda referenciarlo con aria-controls */}
      <Sidebar id="sidebar" isOpen={sidebarOpen} onClose={closeSidebar} />

      <div className="flex-1 flex flex-col">
        {/* Skip link (visible al foco) para accesibilidad */}
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-white p-2 rounded shadow"
        >
          Saltar al contenido
        </a>

        {/* Pasamos sidebarOpen para controlar aria-expanded en Header */}
        <Header toggleSidebar={openSidebar} sidebarOpen={sidebarOpen} />

        <main id="main-content" className="p-6 flex-1" tabIndex={-1}>
          <AnimatePresence mode="wait" initial={false}>
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.22 }}
            >
              {/* Cada componente de ruta idealmente debe usar su propio <header>/<h1> */}
              <Routes location={location} key={location.pathname}>
                <Route path="profile" element={<Profile />} />
                <Route path="orders" element={<Ordenes />} />
                <Route path="cart" element={<Carrito />} />
                <Route path="settings" element={<Configuraciones />} />
                <Route index element={<ProductList />} />
              </Routes>
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}
