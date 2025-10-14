// src/modulos/productos/ProductoForm.jsx
import React, { useState, useEffect } from "react";

/*
 Props:
  - productoInicial: objeto con datos (para editar)
  - categoriasDisponibles: array {id, nombre} (opcional)
  - onSubmit({ datos, imagenes }) -> Promise
  - onCancelar()
*/
export default function ProductoForm({ productoInicial = null, categoriasDisponibles = [], onSubmit, onCancelar }) {
  const [datos, setDatos] = useState({
    nombre: "",
    codigo: "",
    descripcion: "",
    precio: "",
    costo: "",
    moneda: "BOB",
    peso: "",
    dimensiones: "",
    activo: true,
    destacado: false,
    categoria_ids: [],
    meta_titulo: "",
    meta_descripcion: ""
  });

  // imagenes: array de { file, preview, texto_alt, es_principal, orden, existingUrl (opcional for edit) }
  const [imagenes, setImagenes] = useState([]);

  useEffect(() => {
    if (productoInicial) {
      // mapear categorías si vienen
      setDatos(prev => ({
        ...prev,
        nombre: productoInicial.nombre ?? "",
        codigo: productoInicial.codigo ?? "",
        descripcion: productoInicial.descripcion ?? "",
        precio: productoInicial.precio ?? "",
        costo: productoInicial.costo ?? "",
        moneda: productoInicial.moneda ?? "BOB",
        peso: productoInicial.peso ?? "",
        dimensiones: productoInicial.dimensiones ?? "",
        activo: productoInicial.activo ?? true,
        destacado: productoInicial.destacado ?? false,
        categoria_ids: (productoInicial.categorias || []).map(c => c.id),
        meta_titulo: productoInicial.meta_titulo ?? "",
        meta_descripcion: productoInicial.meta_descripcion ?? "",
      }));

      // set imagenes existentes para previsualizar (solo visual; para editar se reenvían si se quiere)
      if (productoInicial.imagenes && productoInicial.imagenes.length) {
        setImagenes(productoInicial.imagenes.map((img, idx) => ({
          file: null,
          preview: img.imagen,
          texto_alt: img.texto_alt ?? "",
          es_principal: img.es_principal ?? false,
          orden: img.orden ?? idx,
          existingUrl: img.imagen
        })));
      }
    }
  }, [productoInicial]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    const val = type === "checkbox" ? checked : value;
    setDatos(prev => ({ ...prev, [name]: val }));
  };

  const handleCategorias = (e) => {
    const opciones = Array.from(e.target.selectedOptions).map(o => Number(o.value));
    setDatos(prev => ({ ...prev, categoria_ids: opciones }));
  };

  const handleAddImages = (e) => {
    const files = Array.from(e.target.files);
    const nuevas = files.map((file, idx) => ({
      file,
      preview: URL.createObjectURL(file),
      texto_alt: file.name,
      es_principal: false,
      orden: imagenes.length + idx
    }));
    setImagenes(prev => [...prev, ...nuevas]);
  };

  const handleRemoveImage = (index) => {
    setImagenes(prev => {
      const copy = [...prev];
      // revoke object URL if exists
      if (copy[index] && copy[index].preview && copy[index].file) {
        URL.revokeObjectURL(copy[index].preview);
      }
      copy.splice(index, 1);
      return copy;
    });
  };

  const handleImageChange = (index, campo, valor) => {
    setImagenes(prev => prev.map((it, i) => i === index ? { ...it, [campo]: valor } : it));
  };

  const submit = async (e) => {
    e.preventDefault();
    // Validaciones simples
    if (!datos.nombre) return alert("Nombre requerido");

    // Preparar payload conforme a productosService.buildProductoFormData
    const payload = {
      datos: { ...datos },
      imagenes: imagenes.map(img => ({
        file: img.file, texto_alt: img.texto_alt, es_principal: !!img.es_principal, orden: img.orden
      }))
    };

    await onSubmit(payload);
  };

  return (
    <form onSubmit={submit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div>
          <label className="block text-sm">Nombre</label>
          <input name="nombre" value={datos.nombre} onChange={handleChange} className="w-full border rounded p-2" />
        </div>
        <div>
          <label className="block text-sm">Código / SKU</label>
          <input name="codigo" value={datos.codigo} onChange={handleChange} className="w-full border rounded p-2" />
        </div>

        <div className="md:col-span-2">
          <label className="block text-sm">Descripción</label>
          <textarea name="descripcion" value={datos.descripcion} onChange={handleChange} className="w-full border rounded p-2" />
        </div>

        <div>
          <label className="block text-sm">Precio</label>
          <input type="number" name="precio" value={datos.precio} onChange={handleChange} step="0.01" className="w-full border rounded p-2" />
        </div>
        <div>
          <label className="block text-sm">Costo</label>
          <input type="number" name="costo" value={datos.costo} onChange={handleChange} step="0.01" className="w-full border rounded p-2" />
        </div>

        <div>
          <label className="block text-sm">Moneda</label>
          <input name="moneda" value={datos.moneda} onChange={handleChange} className="w-full border rounded p-2" />
        </div>

        <div>
          <label className="block text-sm">Stock (se maneja con almacenes, pero campo opcional)</label>
          <input name="stock" disabled placeholder="Stock se calcula por almacenes" className="w-full border rounded p-2 bg-gray-50" />
        </div>

        <div>
          <label className="block text-sm">Categorías</label>
          <select multiple value={datos.categoria_ids.map(String)} onChange={handleCategorias} className="w-full border rounded p-2 h-32">
            {(Array.isArray(categoriasDisponibles) ? categoriasDisponibles : []).map(cat => (
                <option key={cat.id} value={cat.id}>{cat.nombre}</option>
            ))}
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm">Imágenes (puedes agregar varias)</label>
        <input type="file" accept="image/*" multiple onChange={handleAddImages} className="mt-2" />
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-3">
          {imagenes.map((img, idx) => (
            <div key={idx} className="border p-2 rounded">
              <div className="h-32 mb-2 overflow-hidden">
                {img.preview ? <img src={img.preview} alt={img.texto_alt} className="w-full h-full object-cover" /> : <div className="w-full h-full bg-gray-100" />}
              </div>
              <input className="w-full border rounded p-1 text-sm mb-1" value={img.texto_alt} onChange={(e) => handleImageChange(idx, "texto_alt", e.target.value)} />
              <div className="flex items-center justify-between text-sm">
                <label className="flex items-center"><input type="checkbox" checked={img.es_principal} onChange={(e) => handleImageChange(idx, "es_principal", e.target.checked)} className="mr-2" />Principal</label>
                <button type="button" onClick={() => handleRemoveImage(idx)} className="text-red-600">Eliminar</button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="flex justify-end space-x-2">
        <button type="button" onClick={onCancelar} className="px-4 py-2 rounded border">Cancelar</button>
        <button type="submit" className="px-4 py-2 rounded bg-indigo-600 text-white">Guardar</button>
      </div>
    </form>
  );
}
