// src/modulos/productos/ProductoForm.jsx
import React, { useState, useEffect } from "react";
import api from "../../services/api"; // tu wrapper axios (añadido)
 
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

  const [imagenes, setImagenes] = useState([]);
  const [almacenesDisponibles, setAlmacenesDisponibles] = useState([]);
  const [almacenesStock, setAlmacenesStock] = useState({}); // { almacenId: cantidad }

  useEffect(() => {
    // cargar almacenes disponibles
    (async () => {
      try {
        const r = await api.get("/productos/almacenes/");
        const data = r.data;
        const lista = Array.isArray(data) ? data : (data.results || []);
        setAlmacenesDisponibles(lista);
        // si hay producto inicial, mapear stocks si vienen
        if (productoInicial && productoInicial.almacenes) {
          const mapa = {};
          productoInicial.almacenes.forEach(a => {
            if (a.almacen && a.cantidad != null) {
              mapa[a.almacen.id || a.almacen] = a.cantidad;
            } else if (a.almacen && a.almacen.id) {
              mapa[a.almacen.id] = a.cantidad;
            }
          });
          setAlmacenesStock(mapa);
        }
      } catch (err) {
        console.warn("No se pudieron cargar almacenes", err);
      }
    })();
  }, [productoInicial]);

  useEffect(() => {
    if (productoInicial) {
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

      if (productoInicial.imagenes && productoInicial.imagenes.length) {
        setImagenes(productoInicial.imagenes.map((img, idx) => ({
          file: null,
          preview: img.imagen_url || null,
          texto_alt: img.texto_alt ?? "",
          es_principal: img.es_principal ?? false,
          orden: img.orden ?? idx,
          existingUrl: img.imagen_url
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
      orden: imagenes.length + idx,
    }));
    setImagenes(prev => [...prev, ...nuevas]);
  };

  const handleRemoveImage = (index) => {
    setImagenes(prev => {
      const copy = [...prev];
      if (copy[index] && copy[index].preview && copy[index].file) {
        URL.revokeObjectURL(copy[index].preview);
      }
      copy.splice(index, 1);
      return copy;
    });
  };

  const handleImageChange = (index, campo, valor) => {
    setImagenes(prev => {
        let newImages = [...prev];
        // Si se está marcando una imagen como principal
        if (campo === "es_principal" && valor === true) {
            // Desmarcar todas las demás
            newImages = newImages.map(img => ({ ...img, es_principal: false }));
        }
        // Aplicar el cambio a la imagen específica
        newImages[index] = { ...newImages[index], [campo]: valor };
        return newImages;
    });
  };

  const handleStockChange = (almacenId, value) => {
    setAlmacenesStock(prev => ({ ...prev, [almacenId]: value }));
  };

  const submit = async (e) => {
    e.preventDefault();
    if (!datos.nombre) return alert("Nombre requerido");

    // 1. Separa los archivos nuevos de las imágenes existentes que se conservan
    const nuevosArchivos = imagenes.filter(img => img.file).map(img => img.file);
    
    // 2. Recolecta las imágenes existentes que el usuario no eliminó
    // Tu serializer espera el payload completo de la imagen para saber qué conservar
    const imagenesExistentes = imagenes
      .filter(img => img.existingUrl)
      .map(img => ({
        url: img.existingUrl,
        texto_alt: img.texto_alt,
        es_principal: img.es_principal,
        orden: img.orden,
      }));

    // 3. Construye el payload de stock
    const almacenes_stock = Object.entries(almacenesStock)
      .map(([almacenId, cantidad]) => ({ 
        almacen: Number(almacenId), 
        cantidad: Number(cantidad || 0) 
      }))
      .filter(it => it.cantidad && it.cantidad > 0);

    // 4. Prepara el payload final para la función onSubmit
    // Esto coincide con lo que esperan tus funciones de servicio
    const payload = {
      datos: { ...datos }, // Enviamos stock dentro de datos
      nuevosArchivos, // Los archivos nuevos
      imagenesExistentes, // Las imágenes que ya estaban y se quedan
      almacenes_stock,
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
          <label className="block text-sm">Stock (se maneja con almacenes)</label>
          <div className="text-xs text-gray-500">Introduce stock inicial por almacén en la sección abajo.</div>
          <input name="stock" disabled placeholder="Stock se calcula por almacenes" className="w-full border rounded p-2 bg-gray-50 mt-1" />
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
        <label className="block text-sm font-medium mb-2">Stock inicial por almacén (opcional)</label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {almacenesDisponibles.map(a => (
            <div key={a.id} className="border p-2 rounded">
              <div className="font-medium">{a.nombre}</div>
              <div className="text-xs text-gray-500 mb-2">{a.codigo}</div>
              <input type="number" min="0" value={almacenesStock[a.id] ?? ""} onChange={(e) => handleStockChange(a.id, e.target.value)} placeholder="Cantidad inicial" className="w-full border p-2 rounded" />
            </div>
          ))}
          {almacenesDisponibles.length === 0 && <div className="text-sm text-gray-500">No hay almacenes configurados.</div>}
        </div>
      </div>

      <div>
        <label className="block text-sm">Imágenes (se subirán a Cloudinary)</label>
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
