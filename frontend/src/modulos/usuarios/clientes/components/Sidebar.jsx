//src/modulos/usuarios/clientes/components/Sidebar.jsx
import React, { useEffect, useRef } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { User, ShoppingCart, Package, Settings, LogOut, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const navLinks = [
  { icon: User, text: 'Mi Perfil', path: '/profile' },
  { icon: Package, text: 'Mis Pedidos', path: '/orders' },
  { icon: ShoppingCart, text: 'Mi Carrito', path: '/cart' },
  { icon: Settings, text: 'Configuración', path: '/settings' },
];

export default function Sidebar({ isOpen = false, onClose = () => {} }) {
  const location = useLocation();
  const panelRef = useRef(null);

  useEffect(() => {
    // Cerrar al cambiar de ruta (útil en móvil)
    onClose();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.pathname]);

  useEffect(() => {
    // Bloquea scroll cuando abierto
    if (isOpen) {
      const original = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
      return () => { document.body.style.overflow = original; };
    }
  }, [isOpen]);

  // Focus trap simple + Escape
  useEffect(() => {
    if (!isOpen) return;
    const node = panelRef.current;
    const focusableSelector = 'a,button,input,textarea,select,[tabindex]:not([tabindex="-1"])';
    const focusable = node ? Array.from(node.querySelectorAll(focusableSelector)) : [];
    if (focusable.length) focusable[0].focus();

    const onKey = (e) => {
      if (e.key === 'Escape') onClose();
      if (e.key === 'Tab' && focusable.length) {
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault(); last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault(); first.focus();
        }
      }
    };

    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [isOpen, onClose]);

  const overlayVars = { hidden: { opacity: 0 }, visible: { opacity: 1 }, exit: { opacity: 0 } };
  const panelVars = { hidden: { x: '-100%' }, visible: { x: 0 }, exit: { x: '-100%' } };

  // Sidebar para desktop (semántico)
  const DesktopSidebar = (
    <aside className="hidden md:flex md:flex-col md:w-64 md:pt-6 md:pb-6 md:bg-white md:shadow" aria-label="Barra lateral">
      <div className="px-6 pb-4 border-b flex items-center gap-3">
        <a href="/" className="flex items-center gap-3" aria-label="Ir al inicio">
          <img src="/logo.svg" alt="Logo MiCuenta" className="w-10 h-10" />
          <h2 className="text-lg font-semibold">MiCuenta</h2>
        </a>
      </div>

      <nav className="flex-1 px-4 py-6" aria-label="Navegación principal">
        <ul className="space-y-1">
          {navLinks.map(l => (
            <li key={l.text}>
              <NavLink
                to={l.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2 rounded-md transition ${
                    isActive ? 'bg-blue-600 text-white' : 'text-gray-700 hover:bg-gray-100'
                  }`
                }
                aria-current={({ isActive }) => (isActive ? 'page' : undefined)}
              >
                <l.icon size={18} aria-hidden="true" />
                <span className="text-sm">{l.text}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      <footer className="px-4 pb-6">
        <button
          className="w-full flex items-center gap-3 px-3 py-2 rounded-md text-gray-700 hover:bg-red-50"
          type="button"
        >
          <LogOut size={18} aria-hidden="true" />
          <span className="text-sm">Cerrar sesión</span>
        </button>
      </footer>
    </aside>
  );

  return (
    <>
      {DesktopSidebar}

      <AnimatePresence>
        {isOpen && (
          <>
            <motion.div
              key="overlay"
              initial="hidden"
              animate="visible"
              exit="exit"
              variants={overlayVars}
              transition={{ duration: 0.16 }}
              className="fixed inset-0 bg-black/40 z-40 md:hidden"
              onClick={onClose}
              aria-hidden="true"
            />

            <motion.aside
              key="panel"
              ref={panelRef}
              initial="hidden"
              animate="visible"
              exit="exit"
              variants={panelVars}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              className="fixed inset-y-0 left-0 z-50 w-72 bg-white shadow-lg md:hidden overflow-auto"
              role="dialog"
              aria-modal="true"
              aria-label="Menú lateral de navegación"
            >
              <div className="flex items-center justify-between px-4 py-3 border-b">
                <a href="/" className="flex items-center gap-3" aria-label="Ir al inicio">
                  <img src="/logo.svg" alt="Logo MiCuenta" className="w-8 h-8" />
                  <h3 className="text-lg font-medium">MiCuenta</h3>
                </a>

                <button onClick={onClose} aria-label="Cerrar menú" className="p-2 rounded hover:bg-gray-100">
                  <X size={18} aria-hidden="true" />
                </button>
              </div>

              <nav className="p-4" aria-label="Navegación principal">
                <ul className="space-y-1">
                  {navLinks.map(l => (
                    <li key={l.text}>
                      <NavLink
                        to={l.path}
                        className={({ isActive }) =>
                          `flex items-center gap-3 px-3 py-2 rounded-md transition ${
                            isActive ? 'bg-blue-600 text-white' : 'text-gray-700 hover:bg-gray-100'
                          }`
                        }
                        aria-current={({ isActive }) => (isActive ? 'page' : undefined)}
                      >
                        <l.icon size={18} aria-hidden="true" />
                        <span className="text-sm">{l.text}</span>
                      </NavLink>
                    </li>
                  ))}
                </ul>

                <div className="pt-4 border-t mt-4">
                  <footer>
                    <button
                      className="w-full flex items-center gap-3 px-3 py-2 rounded-md text-gray-700 hover:bg-red-50"
                      type="button"
                    >
                      <LogOut size={18} aria-hidden="true" />
                      <span className="text-sm">Cerrar sesión</span>
                    </button>
                  </footer>
                </div>
              </nav>
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
