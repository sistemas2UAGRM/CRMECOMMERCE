import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

export default function ProductosAdd() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    nombre: "",
    descripcion: "",
    precio_venta: "",
    garantia: "",
    activo: true,
    categoria: "",
    stock: ""
  });
  const [error, setError] = useState("");

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await axios.post("/api/v1/ecommerce/productos/", {
        nombre: form.nombre,
        descripcion: form.descripcion,
        precio_venta: form.precio_venta,
        garantia: form.garantia,
        activo: form.activo,
        categoria: form.categoria,
        stock: form.stock
      });
      navigate("/productos");
    } catch (err) {
      setError("Error al crear el producto. Verifica los datos.");
    }
  };

  return (
    <section className="py-12 bg-slate-50 min-h-screen flex items-center justify-center">
      <div className="container max-w-lg mx-auto bg-white p-8 rounded-3xl shadow-xl border border-slate-100">
        <h2 className="text-2xl font-bold mb-6 text-center">Agregar Producto</h2>
        <form className="space-y-5" onSubmit={handleSubmit}>
          <div>
            <label className="block text-slate-700 font-medium mb-2">Nombre</label>
            <input name="nombre" value={form.nombre} onChange={handleChange} required className="w-full px-4 py-2 border rounded-xl" />
          </div>
          <div>
            <label className="block text-slate-700 font-medium mb-2">Descripción</label>
            <textarea name="descripcion" value={form.descripcion} onChange={handleChange} className="w-full px-4 py-2 border rounded-xl" />
          </div>
          <div>
            <label className="block text-slate-700 font-medium mb-2">Precio de venta</label>
            <input name="precio_venta" type="number" step="0.01" value={form.precio_venta} onChange={handleChange} required className="w-full px-4 py-2 border rounded-xl" />
          </div>
          <div>
            <label className="block text-slate-700 font-medium mb-2">Garantía</label>
            <input name="garantia" value={form.garantia} onChange={handleChange} className="w-full px-4 py-2 border rounded-xl" />
          </div>
          <div className="flex items-center gap-2">
            <input name="activo" type="checkbox" checked={form.activo} onChange={handleChange} />
            <label className="text-slate-700 font-medium">Activo</label>
          </div>
          <div>
            <label className="block text-slate-700 font-medium mb-2">Categoría (ID)</label>
            <input name="categoria" type="number" value={form.categoria} onChange={handleChange} required className="w-full px-4 py-2 border rounded-xl" />
          </div>
          <div>
            <label className="block text-slate-700 font-medium mb-2">Stock (ID)</label>
            <input name="stock" type="number" value={form.stock} onChange={handleChange} required className="w-full px-4 py-2 border rounded-xl" />
          </div>
          {error && <div className="text-red-600 text-sm mb-2">{error}</div>}
          <button type="submit" className="w-full bg-blue-600 text-white py-3 rounded-full font-semibold hover:bg-blue-700 transition-all">Guardar</button>
        </form>
      </div>
    </section>
  );
}
