// src/modulos/productos/GestionProductos.jsx
import React, { useState, useEffect } from "react";
import { useProductos } from "./hooks/useProductos";

import ProductoTable from "./ProductoTable";
import Modal from "./Modal";
import ProductoForm from "./ProductoForm";

import api from "../../services/api";

export default function GestionProductos() {
  const {
    productos, cargando, error, obtenerProductos,
    crearProducto, editarProducto, eliminarProducto, pagina, setPagina, meta
  } = useProductos();

  const [abiertoCrear, setAbiertoCrear] = useState(false);
  const [productoEdit, setProductoEdit] = useState(null);
  const [productoDetalle, setProductoDetalle] = useState(null);
  const [categorias, setCategorias] = useState([]);
  const [busqueda, setBusqueda] = useState("");

  useEffect(() => {
    // Cargar categorías para el selector (normaliza paginación si existe)
    (async () => {
      try {
        const r1 = await api.get("/productos/categorias/");
        const datos = r1.data;
        if (Array.isArray(datos)) {
          setCategorias(datos);
        } else if (datos && Array.isArray(datos.results)) {
          setCategorias(datos.results);
        } else {
          // Si no es ninguno de los anteriores, intenta obtener keys con "cat"
          console.warn("Respuesta inesperada al cargar categorias:", datos);
          setCategorias([]);
        }
      } catch (err) {
        console.warn("No se pudo cargar /productos/categorias/:", err);
        setCategorias([]);
      }
    })();
      // eslint-disable-next-line
  }, []);


  // cargar productos al montar y cuando cambie pagina
  useEffect(() => {
    const cargar = async () => {
      try {
        await obtenerProductos();
      } catch (e) {
        console.error("Error al obtener productos:", e);
      }
    };
    cargar();
    // eslint-disable-next-line
  }, [pagina]);

  const abrirEditar = (producto) => setProductoEdit(producto);
  const abrirDetalle = (producto) => setProductoDetalle(producto);

  const handleCrear = async (payload) => {
    try {
      // El 'payload' viene del formulario con { datos, nuevosArchivos }
      // Lo pasamos directamente a la función del hook/servicio.
      // Cambiamos el nombre de la prop de 'archivosDeImagenes' a 'nuevosArchivos' para ser consistentes.
      await crearProducto({ 
          datos: payload.datos, 
          archivosDeImagenes: payload.nuevosArchivos,
          almacenes_stock: payload.almacenes_stock 
      });
      setAbiertoCrear(false);
      alert("Producto creado correctamente");
    } catch (err) {
      console.error(err);
      const msg = err?.response?.data || err.message || "Error creando producto";
      alert(JSON.stringify(msg));
    }
  };

  const handleEditar = async (payload) => {
    try {
      // El 'payload' ahora contiene { datos, nuevosArchivos, imagenesExistentes }
      await editarProducto(productoEdit.id, payload);
      setProductoEdit(null);
      alert("Producto actualizado");
    } catch (err){     
      console.error(err);
      const msg = err?.response?.data || err.message || "Error actualizando producto";
      alert(JSON.stringify(msg));
    }
  };

  const handleEliminar = async (id) => {
    if (!window.confirm("¿Eliminar producto?")) return;
    try {
      await eliminarProducto(id);
      alert("Producto eliminado");
    } catch (err) {
      console.error(err);
      const msg = err?.response?.data || err.message || "Error eliminando producto";
      alert(JSON.stringify(msg));
    }
  };

  // Búsqueda simple que consulta el endpoint con ?search=
  const handleBuscar = async (e) => {
    e.preventDefault();
    try {
      await obtenerProductos({ search: busqueda });
    } catch (err) {
      console.error("Error en búsqueda:", err);
    }
  };

  return (
    <div className="p-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold">Gestión de Productos</h1>
          <p className="text-sm text-gray-500">Administra tus productos, imágenes, categorías y stock por almacén.</p>
        </div>

        <div className="flex items-center gap-3">
          <form onSubmit={handleBuscar} className="hidden sm:flex items-center gap-2">
            <input
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              placeholder="Buscar productos..."
              className="border rounded-full px-3 py-1 text-sm shadow-sm"
            />
            <button type="submit" className="px-3 py-1 bg-gray-200 rounded">Buscar</button>
            <button type="button" onClick={() => { setBusqueda(""); obtenerProductos(); }} className="px-3 py-1 border rounded">Limpiar</button>
          </form>

          <button onClick={() => setAbiertoCrear(true)} className="px-4 py-2 bg-green-600 text-white rounded">Nuevo producto</button>
        </div>
      </div>

      {cargando && <div className="mb-4 text-gray-600">Cargando productos...</div>}
      {error && <div className="mb-4 text-red-600">Error al cargar productos</div>}

      {/* Tabla */}
      <ProductoTable
        productos={productos}
        onVer={abrirDetalle}
        onEditar={abrirEditar}
        onEliminar={handleEliminar}
        cargando={cargando}
      />

      {/* Paginación */}
      {meta && (
        <div className="mt-6 flex justify-between items-center">
          <div>Total: {meta.count}</div>
          <div className="space-x-2">
            <button disabled={!meta.previous} onClick={() => setPagina(p => Math.max(1, p - 1))} className="px-3 py-1 border rounded disabled:opacity-50">Anterior</button>
            <span>Página {pagina}</span>
            <button disabled={!meta.next} onClick={() => setPagina(p => p + 1)} className="px-3 py-1 border rounded disabled:opacity-50">Siguiente</button>
          </div>
        </div>
      )}

      {/* MODALES */}
      <Modal abierto={abiertoCrear} titulo="Crear producto" onCerrar={() => setAbiertoCrear(false)}>
        <ProductoForm
          categoriasDisponibles={categorias}
          onSubmit={handleCrear}
          onCancelar={() => setAbiertoCrear(false)}
        />
      </Modal>

      <Modal abierto={!!productoEdit} titulo="Editar producto" onCerrar={() => setProductoEdit(null)}>
        <ProductoForm
          productoInicial={productoEdit}
          categoriasDisponibles={categorias}
          onSubmit={handleEditar}
          onCancelar={() => setProductoEdit(null)}
        />
      </Modal>

      <Modal abierto={!!productoDetalle} titulo="Detalles del producto" onCerrar={() => setProductoDetalle(null)}>
        {productoDetalle && (
          <div>
            <h3 className="font-semibold text-xl">{productoDetalle.nombre}</h3>
            <p className="text-sm text-gray-600 mb-2">{productoDetalle.descripcion}</p>

            <div className="grid grid-cols-2 gap-3 mb-3">
              {productoDetalle.imagenes && productoDetalle.imagenes.length ? (
                productoDetalle.imagenes.map((img) => (
                  <img key={img.id} src={img.imagen_url} alt={img.texto_alt} className="w-full h-40 object-cover rounded" />
                ))
              ) : (
                <div className="col-span-full text-gray-500">Sin imágenes</div>
              )}
            </div>

            <div className="mt-2 text-sm space-y-1">
              <p><strong>Precio:</strong> Bs {productoDetalle.precio}</p>
              <p><strong>Categorías:</strong> {(productoDetalle.categorias || []).map(c => c.nombre).join(", ")}</p>
              <p><strong>Stock total:</strong> {productoDetalle.almacenes ? productoDetalle.almacenes.reduce((acc,a)=>acc + (a.cantidad||0),0) : productoDetalle.stock_total ?? 0}</p>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
