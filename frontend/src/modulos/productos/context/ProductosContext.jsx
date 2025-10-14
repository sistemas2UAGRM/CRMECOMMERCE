// src/modulos/productos/context/ProductosContext.jsx
import React, { createContext, useState, useEffect } from "react";
import productosService from "../../../services/productosService";

export const ProductosContext = createContext();

export const ProductosProvider = ({ children }) => {
  const [productos, setProductos] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);

  // Paginación simple
  const [pagina, setPagina] = useState(1);
  const [pageSize, setPageSize] = useState(12);
  const [meta, setMeta] = useState(null); // si tu API devuelve count/next/previous

  const obtenerProductos = async (params = {}) => {
    setCargando(true);
    setError(null);
    try {
      const data = await productosService.listar({ page: pagina, page_size: pageSize, ...params });
      // Soporta respuestas tipo DRF paginadas ({ results, count, next, previous })
      if (Array.isArray(data)) {
        setProductos(data);
        setMeta(null);
      } else if (data.results) {
        setProductos(data.results);
        setMeta({ count: data.count, next: data.next, previous: data.previous });
      } else {
        setProductos(data);
      }
    } catch (err) {
      setError(err);
      console.error(err);
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    obtenerProductos();
    // eslint-disable-next-line
  }, [pagina, pageSize]);

  const crearProducto = async (payload) => {
    setCargando(true);
    try {
      const nuevo = await productosService.crear(payload);
      // añadir al inicio
      setProductos(prev => [nuevo, ...prev]);
      return nuevo;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setCargando(false);
    }
  };

  const editarProducto = async (id, payload) => {
    setCargando(true);
    try {
      const actualizado = await productosService.actualizar(id, payload);
      setProductos(prev => prev.map(p => (p.id === id ? actualizado : p)));
      return actualizado;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setCargando(false);
    }
  };

  const eliminarProducto = async (id) => {
    setCargando(true);
    try {
      await productosService.eliminar(id);
      setProductos(prev => prev.filter(p => p.id !== id));
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setCargando(false);
    }
  };

  return (
    <ProductosContext.Provider value={{
      productos, cargando, error, meta, pagina, setPagina, pageSize, setPageSize,
      obtenerProductos, crearProducto, editarProducto, eliminarProducto
    }}>
      {children}
    </ProductosContext.Provider>
  );
};
