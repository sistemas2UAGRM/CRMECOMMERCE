// src/modulos/usuarios/context/UsersContext.jsx
import React, { createContext, useState, useCallback } from "react";
import usersService from "../../../services/usersService";
import toast from "react-hot-toast";

export const UsersContext = createContext();

export const UsersProvider = ({ children }) => {
  const [usuarios, setUsuarios] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);
  const [meta, setMeta] = useState(null); // Para paginación

  const obtenerUsuarios = useCallback(async (params = { page: 1, search: "" }) => {
    setCargando(true);
    setError(null);
    try {
      const data = await usersService.listar(params);
      setUsuarios(data.results || data);
      setMeta({ count: data.count ?? null, next: !!data.next, previous: !!data.previous });
    } catch (err) {
      console.error("Error al obtener usuarios:", err);
      setError(err);
      toast.error("Error al cargar usuarios.");
    } finally {
      setCargando(false);
    }
  }, []);

  const crearUsuario = useCallback(async (payload) => {
    setCargando(true);
    try {
      const nuevo = await usersService.crearPorAdmin(payload);
      setUsuarios(prev => [nuevo, ...prev]);
      toast.success("Usuario creado exitosamente.");
      return nuevo;
    } catch (err) {
      console.error("Error al crear usuario:", err);
      toast.error("Error al crear usuario.");
      throw err; 
    } finally {
      setCargando(false);
    }
  }, []);

  const actualizarUsuario = useCallback(async (id, payload) => {
    setCargando(true);
    try {
      const actualizado = await usersService.actualizar(id, payload);
      setUsuarios(prev => prev.map(u => (u.id === id ? { ...u, ...actualizado } : u)));
      toast.success("Usuario actualizado.");
      return actualizado;
    } catch (err) {
      console.error("Error al actualizar usuario:", err);
      toast.error("Error al actualizar.");
      throw err;
    } finally {
      setCargando(false);
    }
  }, []);

  const eliminarUsuario = useCallback(async (id) => {
    setCargando(true);
    try {
      await usersService.eliminar(id);
      setUsuarios(prev => prev.filter(u => u.id !== id));
      toast.success("Usuario eliminado.");
    } catch (err) {
      console.error("Error al eliminar usuario:", err);
      toast.error("Error al eliminar usuario.");
      throw err;
    } finally {
      setCargando(false);
    }
  }, []);

  const buscarUsuarios = useCallback(async (q) => {
    setCargando(true);
    try {
      const data = await usersService.buscar(q);
      setUsuarios(data.results || data);
      setMeta({
        count: data.count ?? null,
        next: !!data.next,
        previous: !!data.previous,
      });
      return data;
    } catch (err) {
      console.error("buscarUsuarios:", err);
      toast.error("Error en búsqueda.");
      throw err;
    } finally {
      setCargando(false);
    }
  }, []);

  const obtenerStats = useCallback(async () => {
    try {
      const s = await usersService.obtenerStats();
      return s;
    } catch (err) {
      console.error("obtenerStats:", err);
      throw err;
    }
  }, []);

  return (
    <UsersContext.Provider value={{
      usuarios, cargando, error, meta,
      obtenerUsuarios, crearUsuario, actualizarUsuario, 
      eliminarUsuario, buscarUsuarios, obtenerStats
    }}>
      {children}
    </UsersContext.Provider>
  );
};