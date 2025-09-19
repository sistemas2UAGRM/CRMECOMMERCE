import { Routes, Route } from "react-router-dom";
import Login from "../components/login";
import Dashboard from '../components/dashboard';
import Carrito from "../modulos/carrito/carrito";
import Perfiles from "../modulos/usuarios/perfiles";

export default function AppRouter() {
  return (
    <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/login" element={<Login />} />
        <Route path="/perfiles" element={<Perfiles />} />


        <Route path="/carrito" element={<Carrito />} />
    </Routes>
  );
}
