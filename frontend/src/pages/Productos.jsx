import { Link } from "react-router-dom";
import React, { useEffect, useState } from "react";
import API from "../services/api";

export default function ProductosPage() {
  const [productos, setProductos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchProductos() {
      try {
        const res = await API.get("ecommerce/productos/");
        setProductos(res.data);
      } catch (err) {
        //setError("Error al cargar productos");
      } finally {
        setLoading(false);
      }
    }
    fetchProductos();
  }, []);

  return (
    <section className="py-8 bg-slate-50 min-h-screen">
      <div className="container mx-auto px-6">
        <div className="flex justify-end mb-4">
          <Link to="/productos/add" className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold shadow hover:bg-blue-700 transition-all">
            Agregar
          </Link>
        </div>
        <div className="bg-white rounded-3xl shadow-xl border border-slate-100 p-4">
          <div className="overflow-x-auto">
            {loading ? (
              <div className="text-center py-8 text-slate-500">Cargando productos...</div>
            ) : error ? (
              <div className="text-center py-8 text-red-600">{error}</div>
            ) : (
              <table className="min-w-full divide-y divide-slate-200">
                <thead className="bg-slate-100">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-bold text-slate-700">ID</th>
                    <th className="px-4 py-2 text-left text-xs font-bold text-slate-700">Nombre</th>
                    <th className="px-4 py-2 text-left text-xs font-bold text-slate-700">Descripción</th>
                    <th className="px-4 py-2 text-left text-xs font-bold text-slate-700">Precio</th>
                    <th className="px-4 py-2 text-left text-xs font-bold text-slate-700">Garantía</th>
                    <th className="px-4 py-2 text-left text-xs font-bold text-slate-700">Activo</th>
                    <th className="px-4 py-2 text-left text-xs font-bold text-slate-700">Categoría</th>
                    <th className="px-4 py-2 text-left text-xs font-bold text-slate-700">Stock</th>
                    <th className="px-4 py-2 text-left text-xs font-bold text-slate-700">Fecha de creación</th>
                  </tr>
                </thead>
                <tbody>
                  {productos.length === 0 ? (
                    <tr>
                      <td colSpan={9} className="text-center py-8 text-slate-500">No hay productos registrados.</td>
                    </tr>
                  ) : (
                    productos.map((p) => (
                      <tr key={p.id} className="hover:bg-slate-50">
                        <td className="px-4 py-2 text-sm">{p.id}</td>
                        <td className="px-4 py-2 text-sm">{p.nombre}</td>
                        <td className="px-4 py-2 text-sm">{p.descripcion}</td>
                        <td className="px-4 py-2 text-sm">{p.precio_venta}</td>
                        <td className="px-4 py-2 text-sm">{p.garantia}</td>
                        <td className="px-4 py-2 text-sm">{p.activo ? "Sí" : "No"}</td>
                        <td className="px-4 py-2 text-sm">{p.categoria}</td>
                        <td className="px-4 py-2 text-sm">{p.stock}</td>
                        <td className="px-4 py-2 text-sm">{p.fecha_creacion}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
