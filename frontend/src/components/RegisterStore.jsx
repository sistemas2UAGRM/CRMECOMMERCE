import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import tenantService from "../services/tenantService";
import { Store, Globe, User, Mail, Lock } from "lucide-react";
import toast from "react-hot-toast";

export default function RegisterStore() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    tienda_nombre: "",
    subdominio: "",
    first_name: "",
    last_name: "",
    email: "",
    password: ""
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await tenantService.registerTenant(formData);
      toast.success("¡Tienda creada con éxito! Redirigiendo...");
      
      // Redirigir al nuevo subdominio
      // El backend nos devuelve la URL completa (ej: http://pepita.localhost:5173/login)
      setTimeout(() => {
          window.location.href = res.redirect_url;
      }, 2000);
      
    } catch (err) {
      console.error(err);
      const msg = err.response?.data?.detail || 
                  JSON.stringify(err.response?.data) || 
                  "Error al crear la tienda";
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 py-12 px-4">
      <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-xl shadow-lg">
        <div className="text-center">
          <h2 className="text-3xl font-extrabold text-gray-900">Crea tu Tienda</h2>
          <p className="mt-2 text-sm text-gray-600">Comienza tu negocio digital hoy mismo</p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            {/* Datos de la Tienda */}
            <div className="relative">
                <label className="text-sm font-medium text-gray-700">Nombre de la Tienda</label>
                <div className="mt-1 relative rounded-md shadow-sm">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <Store className="h-5 w-5 text-gray-400" />
                    </div>
                    <input name="tienda_nombre" required onChange={handleChange} className="pl-10 block w-full border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-2 border" placeholder="Mi Super Boutique" />
                </div>
            </div>

            <div className="relative">
                <label className="text-sm font-medium text-gray-700">Subdominio deseado</label>
                <div className="mt-1 flex rounded-md shadow-sm">
                    <span className="inline-flex items-center px-3 rounded-l-md border border-r-0 border-gray-300 bg-gray-50 text-gray-500 sm:text-sm">
                        http://
                    </span>
                    <input name="subdominio" required onChange={handleChange} className="flex-1 min-w-0 block w-full px-3 py-2 rounded-none rounded-r-md border border-gray-300 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm" placeholder="pepita" />
                </div>
                <p className="mt-1 text-xs text-gray-500">Tu tienda será: {formData.subdominio || 'ejemplo'}.localhost:5173</p>
            </div>

            <div className="border-t pt-4">
                <p className="text-sm font-medium text-gray-900 mb-4">Datos del Administrador</p>
                
                <div className="grid grid-cols-2 gap-2 mb-3">
                    <input name="first_name" required onChange={handleChange} placeholder="Nombre" className="border p-2 rounded w-full" />
                    <input name="last_name" required onChange={handleChange} placeholder="Apellido" className="border p-2 rounded w-full" />
                </div>
                
                <input name="email" type="email" required onChange={handleChange} placeholder="Correo Electrónico" className="border p-2 rounded w-full mb-3" />
                <input name="password" type="password" required onChange={handleChange} placeholder="Contraseña" className="border p-2 rounded w-full" />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-[#2e7e8b] hover:bg-[#266a75] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-70"
          >
            {loading ? "Creando infraestructura..." : "Lanzar mi Tienda 🚀"}
          </button>
        </form>
      </div>
    </div>
  );
}