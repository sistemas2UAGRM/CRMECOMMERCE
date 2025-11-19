// frontend/src/modulos/usuarios/clientes/dashcliente.jsx
import React, { useState, useEffect } from 'react';
import { Link, Route, Routes, useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Package, ShoppingCart, Settings, Users, LogOut } from 'lucide-react';
import ProductList from './components/ProductoLista';
import Ordenes from './components/Ordenes';
import Carrito from './components/Carrito';
import Configuraciones from './components/Configuraciones';
import Profile from './components/Profile';
import logocrm from '../../../assets/logoCRM.png';
import carritoService from '../../../services/carritosService';
import { clearAuthTokens, getRefreshToken } from '../../../utils/auth';
import api from '../../../services/api';
import toast from 'react-hot-toast';

const sidebarItems = [
  { name: 'Productos', icon: <Package size={22} />, path: '/cliente/productos' },
  { name: 'Mis Pedidos', icon: <Users size={22} />, path: '/cliente/ordenes' },
  { name: 'Mi Carrito', icon: <ShoppingCart size={22} />, path: '/cliente/carrito' },
  { name: 'Configuraciones', icon: <Settings size={22} />, path: '/cliente/configuraciones' },
];

export default function DashCliente() {
  const location = useLocation();
  const navigate = useNavigate(); // Hook para redirección
  const [isCartOpen, setIsCartOpen] = useState(false); // Estado para controlar el sidebar del carrito
  const [cartItems, setCartItems] = useState([]); // Estado para los productos del carrito

  const toggleCart = () => setIsCartOpen(!isCartOpen);

  // Redirigir automáticamente a productos cuando se carga el dashboard
  useEffect(() => {
    if (location.pathname === '/cliente' || location.pathname === '/cliente/') {
      navigate('/cliente/productos', { replace: true });
    }
  }, [location.pathname, navigate]);

  useEffect(() => {
    if (isCartOpen) {
      const fetchCartItems = async () => {
        try {
          const data = await carritoService.obtenerMiCarrito();
          setCartItems(data.items || []);
        } catch (error) {
          console.error('Error al cargar el carrito:', error);
        }
      };
      fetchCartItems();
    }
  }, [isCartOpen]);

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

  return (
    <div className="flex h-screen bg-gray-100 font-sans text-gray-800">
      <aside
        className="w-20 md:w-56 bg-[#2e7e8b] text-white flex flex-col items-center md:items-stretch py-6 shadow-lg transition-all duration-300"
        aria-label="Menú lateral principal"
      >
        <div className="flex items-center justify-center md:justify-start gap-3 px-4 mb-6">
          <Link to="/" className="flex items-center gap-3">
            <img src={logocrm} alt="Logo" className="w-10 h-10 sm:w-12 sm:h-12 md:w-14 md:h-14 object-contain" />
            <span className="hidden md:inline-block font-bold text-xl">MiApp</span>
          </Link>
        </div>

        <nav className="flex-1 w-full px-2 overflow-y-auto custom-scrollbar" aria-label="Navegación principal">
          <ul className="flex flex-col gap-2">
            {sidebarItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <li key={item.name}>
                  <Link
                    to={item.path}
                    title={item.name}
                    aria-current={isActive ? 'page' : undefined}
                    className={`w-full flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors duration-200 transform ${isActive
                      ? 'bg-[#f0a831] text-white shadow-lg'
                      : 'text-gray-200 hover:bg-white/10 hover:text-white'
                      }`}
                  >
                    <span className="flex items-center justify-center">{item.icon}</span>
                    <span className="hidden md:inline-block">{item.name}</span>
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        <div className="mt-auto px-3 py-4">
          <button
            onClick={handleLogout}
            title="Cerrar Sesión"
            className="w-full flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[#2e7e8b] focus:ring-white text-gray-200 hover:bg-red-600 hover:text-white"
          >
            <LogOut size={22} />
            <span className="hidden md:inline-block">Cerrar Sesión</span>
          </button>
        </div>
      </aside>

      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="sticky top-0 z-10 w-full border-b bg-white shadow-sm px-6 py-3">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-semibold text-gray-800">
              {sidebarItems.find((item) => item.path === location.pathname)?.name || 'Dashboard'}
            </h1>
          </div>
        </header>

        <main id="main-content" className="p-6 lg:p-8 flex-1 overflow-y-auto bg-gray-100" tabIndex={-1}>
          <AnimatePresence mode="wait" initial={false}>
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.22 }}
            >
              <Routes location={location} key={location.pathname}>
                <Route path="/cliente/productos" element={<ProductList />} />
                <Route path="/cliente/ordenes" element={<Ordenes />} />
                <Route path="/cliente/carrito" element={<Carrito />} />
                <Route path="/cliente/configuraciones" element={<Configuraciones />} />
                <Route path="/cliente/perfil" element={<Profile />} />
              </Routes>
            </motion.div>
          </AnimatePresence>
        </main>

        {/* Sidebar del carrito */}
        {isCartOpen && (
          <div className="fixed top-0 right-0 h-full w-80 bg-white shadow-lg z-50 flex flex-col">
            <div className="p-4 border-b flex justify-between items-center">
              <h2 className="text-lg font-bold">Mi Carrito</h2>
              <button
                onClick={toggleCart}
                className="text-gray-500 hover:text-gray-800 focus:outline-none"
              >
                ✕
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-4">
              {cartItems.length > 0 ? (
                cartItems.map((item) => (
                  <div key={item.id} className="flex items-center justify-between border-b py-2">
                    <div>
                      <p className="text-sm font-medium text-gray-800">{item.producto.nombre}</p>
                      <p className="text-xs text-gray-500">Cantidad: {item.cantidad}</p>
                    </div>
                    <p className="text-sm font-semibold text-gray-800">${item.producto.precio.toFixed(2)}</p>
                  </div>
                ))
              ) : (
                <p className="text-gray-500">Tu carrito está vacío.</p>
              )}
            </div>
            <div className="p-4 border-t">
              <button
                className="w-full px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Finalizar Compra
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
