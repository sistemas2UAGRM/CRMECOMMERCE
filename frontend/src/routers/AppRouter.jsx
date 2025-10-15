import { Routes, Route } from "react-router-dom";
import Login from "../components/login";
import Register from "../components/registraruser";
import Dashboard from '../components/dashboard';
import DashAdmin from "../components/dashadmin";
import DashCliente from "../components/dashcliente";
import Carrito from "../modulos/carrito/carrito";
import Perfiles from "../modulos/usuarios/perfiles";
import RequireAuth from "../components/RequireAuth";

export default function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/login" element={<Login />} />
      <Route path="/registro" element={<Register />} />
      <Route path="/perfiles" element={<Perfiles />} />
      <Route path="/admin" element={<DashAdmin />} />
      <Route path="/dashboard" element={<DashCliente />} />

      <Route path="/carrito" element={<Carrito />} />
    </Routes>
  );
}
