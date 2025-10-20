// src/modulos/productos/GestionProductos.jsx
import React, { useState, useEffect } from "react";
import { useProductos } from "./hooks/useProductos";
import toast from "react-hot-toast";

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
  const [almacenes, setAlmacenes] = useState([]);
  const [busqueda, setBusqueda] = useState("");

  useEffect(() => {
    // Cargar datos iniciales (categorías y almacenes)
    const cargarDatosIniciales = async () => {
      try {
        const [resCategorias, resAlmacenes] = await Promise.all([
          api.get("/ecommerce/categorias/"),
          api.get("/ecommerce/almacenes/")
        ]);
        
        const procesarRespuesta = (res, nombre) => {
          const datos = res.data;
          if (Array.isArray(datos)) return datos;
          if (datos && Array.isArray(datos.results)) return datos.results;
          console.warn(`Respuesta inesperada al cargar ${nombre}:`, datos);
          return [];
        };
        setCategorias(procesarRespuesta(resCategorias, 'categorías'));
        setAlmacenes(procesarRespuesta(resAlmacenes, 'almacenes'));
      } catch (err) {
        console.warn("No se pudo cargar la configuración inicial:", err);
        setCategorias([]);
        setAlmacenes([]);
      }
    };
    cargarDatosIniciales();
  }, []);


  // cargar productos al montar y cuando cambie pagina
  useEffect(() => {
    const cargar = async () => {
      try {
        await obtenerProductos({ search: busqueda, page: pagina });
      } catch (e) {
        console.error("Error al obtener productos:", e);
        toast.error("No se pudieron cargar los productos.");
      }
    };
    cargar();
  }, [pagina, busqueda, obtenerProductos]);

  const abrirEditar = async (producto) => {
    try {
      const response = await api.get(`/ecommerce/productos/${producto.id}/`);
      setProductoEdit(response.data);
    } catch (error) {
      console.error("Error al cargar los detalles del producto para editar:", error);
      toast.error("No se pudieron cargar los datos del producto.");
    }
  };

  const abrirDetalle = async (producto) => {
        try {
            const response = await api.get(`/ecommerce/productos/${producto.id}/`);
            setProductoDetalle(response.data);
        } catch (error) {
            console.error("Error al cargar los detalles del producto:", error);
            toast.error("No se pudieron cargar los detalles del producto.");
        }
    };
  
  const handleCrear = async (payload) => {
    try {
      await crearProducto({ 
          datos: payload.datos, 
          archivosDeImagenes: payload.nuevosArchivos,
          almacenes_stock: payload.almacenes_stock 
      });
      setAbiertoCrear(false);
      toast.success("Producto creado exitosamente");
    } catch (err) {
      console.error(err);
      const msg = err?.response?.data || err.message || "Error creando producto";
      toast.error(msg);
    }
  };

  const handleEditar = async (payload) => {
    try {
      await editarProducto(productoEdit.id, payload);
      setProductoEdit(null);
      toast.success("Producto actualizado exitosamente");
    } catch (err){     
      console.error(err);
      const msg = err?.response?.data?.detail || err.message || "Error actualizando producto";
      toast.error(msg);
    }
  };

  const handleEliminar = async (id) => {
    if (!window.confirm("¿Estás seguro de que quieres eliminar este producto?")) return;
    try {
      await eliminarProducto(id);
      toast.success("Producto eliminado exitosamente");
    } catch (err) {
      console.error(err);
      const msg = err?.response?.data || err.message || "Error eliminando producto";
      toast.error(msg);
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
          almacenesDisponibles={almacenes}
          onSubmit={handleCrear}
          onCancelar={() => setAbiertoCrear(false)}
        />
      </Modal>

      <Modal abierto={!!productoEdit} titulo="Editar producto" onCerrar={() => setProductoEdit(null)}>
        <ProductoForm
          productoInicial={productoEdit}
          categoriasDisponibles={categorias}
          almacenesDisponibles={almacenes}
          onSubmit={handleEditar}
          onCancelar={() => setProductoEdit(null)}
        />
      </Modal>

      <Modal abierto={!!productoDetalle} titulo="Detalles del producto" onCerrar={() => setProductoDetalle(null)}>
        {productoDetalle && (
          <div>
            <h3 className="font-semibold text-xl">{productoDetalle.nombre}</h3>
            <p className="text-sm text-gray-600 mb-2">{productoDetalle.descripcion}</p>

            <div className="grid grid-cols-2 gap-3 mb-4">
              {productoDetalle.imagenes && productoDetalle.imagenes.length > 0 ? (
                productoDetalle.imagenes.map((img) => (
                  <img key={img.id} src={img.imagen_url} alt={img.texto_alt} className="w-full h-40 object-cover rounded" />
                ))
              ) : (
                <div className="col-span-full text-gray-500">Sin imágenes</div>
              )}
              </div>

            <div className="mt-2 text-sm space-y-1">
              <p><strong>Precio:</strong> {productoDetalle.moneda} {productoDetalle.precio}</p>
              <p><strong>Categorías:</strong> {(productoDetalle.categorias || []).map(c => c.nombre).join(", ")}</p>
              <p><strong>Stock total:</strong> {productoDetalle.stock_total ?? 0}</p>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
