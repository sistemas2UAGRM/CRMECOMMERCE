// src/modulos/productos/context/ProductosContext.jsx
import React, { createContext, useState, useEffect, useCallback } from "react";
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

  const obtenerProductos = useCallback(async (params = {}) => {
    setCargando(true);
    setError(null);
    try {
      // Asumiendo que `listar` acepta un objeto de parámetros
      const data = await productosService.listar({ page: pagina, ...params });
      if (data.results) {
        setProductos(data.results);
        setMeta({ count: data.count, next: data.next, previous: data.previous });
      } else {
        setProductos(Array.isArray(data) ? data : []);
        setMeta(null);
      }
    } catch (err) {
      setError(err);
      console.error(err);
    } finally {
      setCargando(false);
    }
  }, [pagina]);

  const crearProducto = useCallback(async (payload) => {
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
  }, []);

  const editarProducto = useCallback(async (id, payload) => {
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
  }, []);

  const eliminarProducto = useCallback(async (id) => {
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
  }, []);

  useEffect(() => {
    obtenerProductos();
  }, [obtenerProductos]);

  return (
    <ProductosContext.Provider value={{
      productos, cargando, error, meta, pagina, setPagina, pageSize, setPageSize,
      obtenerProductos, crearProducto, editarProducto, eliminarProducto
    }}>
      {children}
    </ProductosContext.Provider>
  );
};
