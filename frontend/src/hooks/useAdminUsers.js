// src/hooks/useAdminUsers.js
import { useState, useEffect, useCallback, useRef } from "react";
import {
  adminListUsers,
  adminDeleteUser,
  adminActivateUser,
  adminDeactivateUser
} from "../services/usersService";

/**
 * Hook para listar usuarios administracion (paginación DRF page)
 * Devuelve: { data, results, count, next, previous, loading, error, refresh, remove, activate, deactivate, params, goPage, setSearch }
 */
export default function useAdminUsers(initialParams = { page: 1, page_size: 10, search: "" }) {
  const [params, setParams] = useState(initialParams);
  const paramsRef = useRef(initialParams); // mantiene referencia actual sin forzar dependencias
  const [data, setData] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // fetch estable: usamos paramsRef para leer los params actuales
  const fetch = useCallback(async (override = {}) => {
    setLoading(true);
    setError(null);
    try {
      const merged = { ...paramsRef.current, ...override };
      const res = await adminListUsers(merged);
      const payload = res.data;
      setData(payload);
      setResults(payload.results ?? payload);
      // Actualizamos estado y ref con el merged
      setParams(merged);
      paramsRef.current = merged;
    } catch (err) {
      setError(err.response?.data || { detail: "Error al obtener usuarios" });
      // No relanzamos: dejamos que el componente consumidor vea `error`.
    } finally {
      setLoading(false);
    }
  }, []); // [] -> función estable, no cambia

  // carga inicial (se ejecuta solo al montar)
  useEffect(() => {
    fetch();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const refresh = () => fetch();
  const goPage = (page) => fetch({ page });

  // Mejorar setSearch para manejar parámetros complejos
  const setSearch = (searchOrParams) => {
    if (typeof searchOrParams === 'string') {
      fetch({ page: 1, search: searchOrParams });
    } else {
      // Si es un objeto, aplicar todos los parámetros
      fetch({ page: 1, ...searchOrParams });
    }
  };

  const remove = async (id) => {
    await adminDeleteUser(id);
    await fetch();
  };

  const activate = async (id) => {
    await adminActivateUser(id);
    await fetch();
  };

  const deactivate = async (id) => {
    await adminDeactivateUser(id);
    await fetch();
  };

  return {
    data,
    results,
    loading,
    error,
    params,
    refresh,
    goPage,
    setSearch,
    remove,
    activate,
    deactivate
  };
}
