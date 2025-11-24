// frontend/src/modulos/productos/hooks/useCategorias.js
import { useState, useEffect } from "react";
import categoriasService from "../../../services/categoriasService";

export const useCategorias = () => {
  const [categorias, setCategorias] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);

  const obtenerCategorias = async () => {
    setCargando(true);
    try {
      const data = await categoriasService.listar();
      if (Array.isArray(data)) {
        setCategorias(data);
      } else if (data && Array.isArray(data.results)) {
        setCategorias(data.results);
      } else {
        setCategorias([]);
        console.warn("Respuesta inesperada al listar categorías:", data);
      }
    } catch (err) {
      console.error(err);
      setError(err);
    } finally {
      setCargando(false);
    }
  };

  const crearCategoria = async (datos) => {
    setCargando(true);
    try {
      const nueva = await categoriasService.crear(datos);
      setCategorias(prev => [...prev, nueva]);
      return nueva;
    } finally {
      setCargando(false);
    }
  };

  const editarCategoria = async (id, datos) => {
    setCargando(true);
    try {
      const actualizada = await categoriasService.actualizar(id, datos);
      setCategorias(prev => prev.map(c => (c.id === id ? actualizada : c)));
      return actualizada;
    } finally {
      setCargando(false);
    }
  };

  const eliminarCategoria = async (id) => {
    setCargando(true);
    try {
      await categoriasService.eliminar(id);
      setCategorias(prev => prev.filter(c => c.id !== id));
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    obtenerCategorias();
  }, []);

  return {
    categorias,
    cargando,
    error,
    obtenerCategorias,
    crearCategoria,
    editarCategoria,
    eliminarCategoria,
  };
};
