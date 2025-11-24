// frontend/src/routers/AppRouter.jsx
import { Routes, Route, Navigate } from "react-router-dom";
import { useTenant } from "../contexts/TenantContext";

// Componentes SaaS (Landing)
import DashboardLanding from '../components/dashboard'; 
import Register from "../components/registraruser";

// Componentes Tenant (Tienda del Cliente)
import Login from "../components/login";
import DashAdmin from "../components/dashadmin";
import DashCliente from "../modulos/usuarios/clientes/dashcliente";
import RequireAuth from "../components/RequireAuth";
import RegisterStore from "../components/RegisterStore";

export default function AppRouter() {
  const { isMainDomain, tenant } = useTenant();

  // --- RUTAS DEL SITIO PRINCIPAL (SAAS - Venta del Software) ---
  if (isMainDomain) {
    return (
      <Routes>
        <Route path="/" element={<DashboardLanding />} />
        <Route path="/registro" element={<RegisterStore />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    );
  }

  // --- RUTAS DEL INQUILINO (TIENDA ESPECÍFICA) ---
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<Login tenantName={tenant?.name} />} />
      <Route path="/registro" element={<Register />} />

      {/* Rutas Protegidas Admin */}
      <Route element={<RequireAuth requiredRole="administrador" />}>
        <Route path="/admin/*" element={<DashAdmin />} />
      </Route>

      {/* Rutas Protegidas Cliente de la Tienda */}
      <Route element={<RequireAuth requiredRole="cliente" />}>
        <Route path="/cliente/*" element={<DashCliente />} />
      </Route>

      {/* PANTALLA DE ERROR 404 (Para saber si caemos en el limbo) */}
    <Route path="*" element={
        <div className="p-10 text-center">
            <h2 className="text-xl font-bold">404 - Ruta no encontrada en el Tenant</h2>
            <p>Estás intentando acceder a: {window.location.pathname}</p>
            <a href="/login" className="text-blue-500 underline">Volver al Login</a>
        </div>
    } />
    </Routes>
  );
}
