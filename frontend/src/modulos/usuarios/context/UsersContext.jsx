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

  const obtenerUsuarios = useCallback(async (params = {}) => {
    setCargando(true);
    setError(null);
    try {
      const data = await usersService.listar(params);
      setUsuarios(data.results || []);
      setMeta({ count: data.count, next: data.next, previous: data.previous });
    } catch (err) {
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
      const nuevo2 = await usersService.adminCreateUser(payload);
      // Opcional: recargar la lista para ver el nuevo usuario
      await obtenerUsuarios(); 
      toast.success("Usuario creado exitosamente.");
      return nuevo;
      
    } catch (err) {
      setError(err);
      toast.error(err.response?.data?.detail || "Error al crear usuario.");
      throw err; // Relanzamos para que el formulario pueda manejarlo
    } finally {
      setCargando(false);
    }
  }, [obtenerUsuarios]);

  const actualizarUsuario = useCallback(async (id, payload) => {
    setCargando(true);
    try {
      const actualizado = await usersService.actualizar(id, payload);
      setUsuarios(prev => prev.map(u => (u.id === id ? { ...u, ...actualizado } : u)));
      toast.success("Usuario actualizado.");
      return actualizado;
    } catch (err) {
      setError(err);
      toast.error(err.response?.data?.detail || "Error al actualizar.");
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
      setError(err);
      toast.error("Error al eliminar usuario.");
      throw err;
    } finally {
      setCargando(false);
    }
  }, []);

  return (
    <UsersContext.Provider value={{
      usuarios, cargando, error, meta,
      obtenerUsuarios, crearUsuario, actualizarUsuario, eliminarUsuario
    }}>
      {children}
    </UsersContext.Provider>
  );
};