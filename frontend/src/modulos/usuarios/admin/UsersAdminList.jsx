// src/pages/admin/UsersAdminList.jsx
import React, { useEffect, useState } from "react";
import useAdminUsers from "../../../hooks/useAdminUsers";
import {
  adminGetUser,
  adminGetActivityLog,
  adminCreateUser,
  adminUpdateUser,
} from "../../../services/adminUsers";
import {
  Users,
  Search,
  Plus,
  RefreshCw,
  Eye,
  Edit2,
  Trash2,
  UserCheck,
  UserX,
  X,
  Save,
  ChevronLeft,
  ChevronRight,
  Mail,
  Phone,
  Calendar,
  Shield,
  Activity,
  AlertCircle,
  Filter,
  FilterX,
  SlidersHorizontal,
  ChevronDown,
  ChevronUp
} from "lucide-react";

/**
 * Versión mejorada con mejor estética usando Tailwind CSS
 * Modal único para ver/editar/crear usuarios
 */

export default function UsersAdminList() {
  const { results, loading, error, data, goPage, setSearch, remove, activate, deactivate, refresh } = useAdminUsers();
  const [q, setQ] = useState("");

  const [mode, setMode] = useState("list"); // 'list' | 'view' | 'edit' | 'new'
  const [selectedId, setSelectedId] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  // Estados para filtros avanzados
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    rol: "",
    is_active: "",
    ordering: "-date_joined"
  });
  const [searchTimeout, setSearchTimeout] = useState(null);

  // Limpiar timeout al desmontar componente
  useEffect(() => {
    return () => {
      if (searchTimeout) {
        clearTimeout(searchTimeout);
      }
    };
  }, [searchTimeout]);

  // Datos para modal
  const [modalLoading, setModalLoading] = useState(false);
  const [userData, setUserData] = useState(null);
  const [userLog, setUserLog] = useState([]);
  const [form, setForm] = useState({
    username: "",
    email: "",
    first_name: "",
    last_name: "",
    fecha_de_nacimiento: "",
    sexo: "",
    celular: "",
    rol: "cliente",
    password: ""
  });
  const [errors, setErrors] = useState({});

  // Buscar con filtros
  const handleSearch = (e) => {
    e?.preventDefault();
    performSearch();
  };

  const performSearch = () => {
    const searchParams = {
      search: q,
      ...filters
    };
    // Filtrar parámetros vacíos
    Object.keys(searchParams).forEach(key => {
      if (searchParams[key] === "" || searchParams[key] == null) {
        delete searchParams[key];
      }
    });
    setSearch(searchParams);
  };

  // Búsqueda en tiempo real con debounce
  const handleSearchInputChange = (value) => {
    setQ(value);

    // Cancelar búsqueda anterior si existe
    if (searchTimeout) {
      clearTimeout(searchTimeout);
    }

    // Nueva búsqueda después de 500ms
    const timeout = setTimeout(() => {
      const searchParams = {
        search: value,
        ...filters
      };
      Object.keys(searchParams).forEach(key => {
        if (searchParams[key] === "" || searchParams[key] == null) {
          delete searchParams[key];
        }
      });
      setSearch(searchParams);
    }, 500);

    setSearchTimeout(timeout);
  };

  // Manejar cambios en filtros
  const handleFilterChange = (filterKey, value) => {
    const newFilters = { ...filters, [filterKey]: value };
    setFilters(newFilters);

    // Aplicar filtros inmediatamente
    const searchParams = {
      search: q,
      ...newFilters
    };
    Object.keys(searchParams).forEach(key => {
      if (searchParams[key] === "" || searchParams[key] == null) {
        delete searchParams[key];
      }
    });
    setSearch(searchParams);
  };

  // Limpiar todos los filtros
  const clearFilters = () => {
    setQ("");
    setFilters({
      rol: "",
      is_active: "",
      ordering: "-date_joined"
    });
    setSearch({});
  };

  // Contar filtros activos
  const getActiveFiltersCount = () => {
    let count = 0;
    if (q) count++;
    if (filters.rol) count++;
    if (filters.is_active !== "") count++;
    return count;
  };

  // Abrir modal ver/editar/nuevo
  const openView = async (id) => {
    setMode("view"); setSelectedId(id); await loadUserIntoModal(id);
  };
  const openEdit = async (id) => {
    setMode("edit"); setSelectedId(id); await loadUserIntoModal(id);
  };
  const openNew = () => {
    setMode("new"); setSelectedId(null);
    setUserData(null); setUserLog([]); setErrors({});
    setForm({
      username: "", email: "", first_name: "", last_name: "",
      fecha_de_nacimiento: "", sexo: "", celular: "", rol: "cliente", password: ""
    });
  };
  const closeModal = () => {
    setMode("list"); setSelectedId(null); setUserData(null); setUserLog([]); setErrors({});
  };

  // Cargar usuario y actividad en modal
  const loadUserIntoModal = async (id) => {
    setModalLoading(true);
    setUserData(null);
    setUserLog([]);
    setErrors({});
    try {
      const res = await adminGetUser(id);
      setUserData(res.data);
      // llenar form con datos para editar
      setForm({
        username: res.data.username ?? "",
        email: res.data.email ?? "",
        first_name: res.data.first_name ?? "",
        last_name: res.data.last_name ?? "",
        fecha_de_nacimiento: res.data.fecha_de_nacimiento ?? "",
        sexo: res.data.sexo ?? "",
        celular: res.data.celular ?? "",
        rol: res.data.rol_actual?.nombre ?? "cliente",
        password: ""
      });
      // actividad
      try {
        const logRes = await adminGetActivityLog(id);
        setUserLog(logRes.data.recent_activity ?? logRes.data ?? []);
      } catch {
        setUserLog([]);
      }
    } catch (err) {
      alert("No se pudo cargar el usuario");
      closeModal();
    } finally {
      setModalLoading(false);
    }
  };

  // Eliminar
  const handleDelete = async (id, username) => {
    if (!confirm(`¿Eliminar usuario ${username}?`)) return;
    setActionLoading(true);
    try {
      await remove(id);
      alert("Usuario eliminado");
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.error || "No se pudo eliminar");
    } finally {
      setActionLoading(false);
    }
  };

  // Activar/Desactivar
  const handleToggleActive = async (user) => {
    if (user.id == null) return;
    const verb = user.is_active ? "desactivar" : "activar";
    if (!confirm(`${verb[0].toUpperCase() + verb.slice(1)} usuario ${user.username}?`)) return;
    setActionLoading(true);
    try {
      if (user.is_active) await deactivate(user.id);
      else await activate(user.id);
      alert(`Usuario ${user.is_active ? "desactivado" : "activado"}`);
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.error || "Error al cambiar estado");
    } finally {
      setActionLoading(false);
    }
  };

  // Manejo de cambios de form
  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  // Guardar (create / update) desde modal
  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});
    setModalLoading(true);
    try {
      if (mode === "edit" && selectedId) {
        // update
        const payload = {
          username: form.username,
          email: form.email,
          first_name: form.first_name,
          last_name: form.last_name,
          fecha_de_nacimiento: form.fecha_de_nacimiento,
          sexo: form.sexo,
          celular: form.celular,
        };
        await adminUpdateUser(selectedId, payload);
        alert("Usuario actualizado");
      } else if (mode === "new") {
        const payload = {
          username: form.username,
          email: form.email,
          first_name: form.first_name,
          last_name: form.last_name,
          fecha_de_nacimiento: form.fecha_de_nacimiento,
          sexo: form.sexo,
          celular: form.celular,
          rol: form.rol,
          password: form.password || undefined,
          send_welcome_email: false
        };
        await adminCreateUser(payload);
        alert("Usuario creado");
      }
      await refresh();
      closeModal();
    } catch (err) {
      const resp = err.response?.data;
      setErrors(resp || { non_field_errors: ["Error desconocido"] });
    } finally {
      setModalLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header con diseño moderno */}
        <div className="bg-white rounded-2xl shadow-xl p-6 mb-6 border border-slate-200">
          <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-blue-500 to-indigo-600 p-3 rounded-xl shadow-lg">
                <Users className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  Administración de Usuarios
                </h1>
                <p className="text-sm text-slate-600 mt-1">
                  Gestión completa de usuarios del sistema
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={openNew}
                className="flex items-center gap-2 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white px-4 py-2.5 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 font-medium"
              >
                <Plus className="w-5 h-5" />
                Nuevo Usuario
              </button>
              <button
                onClick={() => refresh()}
                className="flex items-center gap-2 bg-white hover:bg-slate-50 border-2 border-slate-200 px-4 py-2.5 rounded-xl shadow-md hover:shadow-lg transition-all duration-200 font-medium text-slate-700"
              >
                <RefreshCw className="w-5 h-5" />
                Refrescar
              </button>
            </div>
          </div>
        </div>

        {/* Búsqueda avanzada mejorada */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-6 border border-slate-200">
          {/* Barra de búsqueda principal */}
          <div className="flex flex-col lg:flex-row gap-4 mb-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
              <input
                value={q}
                onChange={(e) => handleSearchInputChange(e.target.value)}
                placeholder="Buscar por nombre, email, username..."
                className="w-full pl-11 pr-4 py-3 border-2 border-slate-200 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-100 outline-none transition-all duration-200"
              />
            </div>

            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setShowFilters(!showFilters)}
                className={`flex items-center gap-2 px-4 py-3 border-2 rounded-xl font-medium transition-all duration-200 ${showFilters || getActiveFiltersCount() > 0
                    ? "bg-blue-50 border-blue-200 text-blue-700"
                    : "bg-white border-slate-200 text-slate-600 hover:bg-slate-50"
                  }`}
              >
                <Filter className="w-4 h-4" />
                Filtros
                {getActiveFiltersCount() > 0 && (
                  <span className="bg-blue-500 text-white text-xs px-2 py-0.5 rounded-full min-w-[20px] text-center">
                    {getActiveFiltersCount()}
                  </span>
                )}
                {showFilters ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>

              {getActiveFiltersCount() > 0 && (
                <button
                  type="button"
                  onClick={clearFilters}
                  className="flex items-center gap-2 px-4 py-3 bg-red-50 border-2 border-red-200 text-red-700 rounded-xl font-medium hover:bg-red-100 transition-all duration-200"
                >
                  <FilterX className="w-4 h-4" />
                  Limpiar
                </button>
              )}
            </div>
          </div>

          {/* Panel de filtros avanzados */}
          {showFilters && (
            <div className="border-t border-slate-200 pt-4 space-y-4">
              <div className="flex items-center gap-2 mb-3">
                <SlidersHorizontal className="w-4 h-4 text-slate-500" />
                <h4 className="text-sm font-medium text-slate-700">Filtros Avanzados</h4>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Filtro por Rol */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Rol</label>
                  <select
                    value={filters.rol}
                    onChange={(e) => handleFilterChange("rol", e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-100 outline-none transition-all duration-200"
                  >
                    <option value="">Todos los roles</option>
                    <option value="administrador">Administrador</option>
                    <option value="empleadonivel1">Empleado Nivel 1</option>
                    <option value="empleadonivel2">Empleado Nivel 2</option>
                    <option value="cliente">Cliente</option>
                  </select>
                </div>

                {/* Filtro por Estado */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Estado</label>
                  <select
                    value={filters.is_active}
                    onChange={(e) => handleFilterChange("is_active", e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-100 outline-none transition-all duration-200"
                  >
                    <option value="">Todos los estados</option>
                    <option value="true">Activos</option>
                    <option value="false">Inactivos</option>
                  </select>
                </div>

                {/* Filtro por Ordenamiento */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Ordenar por</label>
                  <select
                    value={filters.ordering}
                    onChange={(e) => handleFilterChange("ordering", e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-100 outline-none transition-all duration-200"
                  >
                    <option value="-date_joined">Más recientes</option>
                    <option value="date_joined">Más antiguos</option>
                    <option value="username">Nombre de usuario A-Z</option>
                    <option value="-username">Nombre de usuario Z-A</option>
                    <option value="email">Email A-Z</option>
                    <option value="-email">Email Z-A</option>
                    <option value="first_name">Nombre A-Z</option>
                    <option value="-first_name">Nombre Z-A</option>
                  </select>
                </div>
              </div>

              {/* Indicador de búsqueda en tiempo real */}
              <div className="flex items-center gap-2 text-xs text-slate-500 bg-slate-50 px-3 py-2 rounded-lg">
                <Activity className="w-3 h-3" />
                La búsqueda se actualiza automáticamente mientras escribes
              </div>
            </div>
          )}
        </div>

        {/* Feedback mejorado */}
        {loading && (
          <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-6 rounded-lg flex items-center gap-3">
            <RefreshCw className="w-5 h-5 text-blue-500 animate-spin" />
            <span className="text-blue-700 font-medium">Cargando usuarios...</span>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6 rounded-lg flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-500" />
            <span className="text-red-700 font-medium">Error: {JSON.stringify(error)}</span>
          </div>
        )}

        {/* Tabla mejorada con diseño moderno */}
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-slate-200">
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="bg-gradient-to-r from-slate-50 to-slate-100 border-b-2 border-slate-200">
                  <th className="px-6 py-4 text-left text-xs font-bold text-slate-600 uppercase tracking-wider">ID</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-slate-600 uppercase tracking-wider">Usuario</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-slate-600 uppercase tracking-wider">Nombre Completo</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-slate-600 uppercase tracking-wider">Email</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-slate-600 uppercase tracking-wider">Rol</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-slate-600 uppercase tracking-wider">Estado</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-slate-600 uppercase tracking-wider">Acciones</th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate-100">
                {!results?.length && !loading ? (
                  <tr>
                    <td className="px-6 py-12 text-center text-slate-500" colSpan="7">
                      <Users className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                      <p className="text-lg font-medium">No hay usuarios registrados</p>
                    </td>
                  </tr>
                ) : results.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-50 transition-colors duration-150">
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-slate-100 text-slate-700 font-semibold text-sm">
                        {u.id}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="font-medium text-slate-900">{u.username}</span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-slate-700">{(u.first_name || "") + " " + (u.last_name || "")}</span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2 text-slate-600">
                        <Mail className="w-4 h-4" />
                        <span className="text-sm">{u.email}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-100 text-indigo-700">
                        <Shield className="w-3.5 h-3.5" />
                        {u.rol ?? u.rol_actual?.nombre ?? "—"}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      {u.is_active ? (
                        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-700">
                          <UserCheck className="w-3.5 h-3.5" />
                          Activo
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-red-100 text-red-700">
                          <UserX className="w-3.5 h-3.5" />
                          Inactivo
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => openView(u.id)}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors duration-150 text-sm font-medium"
                        >
                          <Eye className="w-4 h-4" />
                          Ver
                        </button>
                        <button
                          onClick={() => openEdit(u.id)}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors duration-150 text-sm font-medium"
                        >
                          <Edit2 className="w-4 h-4" />
                          Editar
                        </button>
                        <button
                          onClick={() => handleToggleActive(u)}
                          disabled={actionLoading}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 border-2 border-slate-200 hover:bg-slate-50 rounded-lg transition-colors duration-150 text-sm font-medium text-slate-700 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {u.is_active ? <UserX className="w-4 h-4" /> : <UserCheck className="w-4 h-4" />}
                          {u.is_active ? "Desactivar" : "Activar"}
                        </button>
                        <button
                          onClick={() => handleDelete(u.id, u.username)}
                          disabled={actionLoading}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-red-600 hover:bg-red-50 rounded-lg transition-colors duration-150 text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <Trash2 className="w-4 h-4" />
                          Eliminar
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Paginación mejorada */}
        {data && (
          <div className="mt-6 bg-white rounded-2xl shadow-lg p-4 border border-slate-200">
            <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
              <div className="text-sm text-slate-600">
                Total de usuarios: <span className="font-bold text-slate-900">{data.count ?? "—"}</span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  disabled={!data.previous}
                  onClick={() => goPage(Math.max(1, getQueryPage(data.previous) - 1))}
                  className="inline-flex items-center gap-2 px-4 py-2 border-2 border-slate-200 rounded-xl hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-medium text-slate-700"
                >
                  <ChevronLeft className="w-4 h-4" />
                  Anterior
                </button>
                <div className="px-5 py-2 bg-gradient-to-r from-blue-500 to-indigo-500 text-white rounded-xl font-semibold shadow-md">
                  Página {currentPageFromData(data)}
                </div>
                <button
                  disabled={!data.next}
                  onClick={() => goPage(getQueryPage(data.next) + 1)}
                  className="inline-flex items-center gap-2 px-4 py-2 border-2 border-slate-200 rounded-xl hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-medium text-slate-700"
                >
                  Siguiente
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ------------------ MODAL MEJORADO ------------------ */}
        {mode !== "list" && (
          <>
            <div className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm" onClick={closeModal} />
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
              <div className="w-full max-w-3xl bg-white rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200" role="dialog" aria-modal="true">
                {/* Header del modal */}
                <div className="flex items-center justify-between p-6 bg-gradient-to-r from-blue-500 to-indigo-600 text-white">
                  <div className="flex items-center gap-3">
                    {mode === "view" && <Eye className="w-6 h-6" />}
                    {mode === "edit" && <Edit2 className="w-6 h-6" />}
                    {mode === "new" && <Plus className="w-6 h-6" />}
                    <h3 className="text-xl font-bold">
                      {mode === "view" && "Ver Usuario"}
                      {mode === "edit" && "Editar Usuario"}
                      {mode === "new" && "Nuevo Usuario"}
                    </h3>
                  </div>
                  <button
                    onClick={closeModal}
                    className="p-2 hover:bg-white/20 rounded-lg transition-colors duration-200"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>

                <div className="p-6 max-h-[calc(100vh-200px)] overflow-y-auto">
                  {modalLoading ? (
                    <div className="flex flex-col items-center justify-center py-12">
                      <RefreshCw className="w-12 h-12 text-blue-500 animate-spin mb-4" />
                      <p className="text-slate-600 font-medium">Cargando información...</p>
                    </div>
                  ) : (
                    <>
                      {mode === "view" && userData && (
                        <div className="space-y-6">
                          {/* Información del usuario */}
                          <div className="bg-gradient-to-br from-slate-50 to-blue-50 rounded-xl p-6 space-y-4">
                            <div className="flex items-center gap-3 pb-3 border-b-2 border-blue-200">
                              <Users className="w-5 h-5 text-blue-600" />
                              <h4 className="font-bold text-lg text-slate-800">Información Personal</h4>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              <div className="flex items-start gap-3">
                                <div className="p-2 bg-white rounded-lg">
                                  <Users className="w-5 h-5 text-slate-600" />
                                </div>
                                <div>
                                  <p className="text-xs font-semibold text-slate-500 uppercase">Usuario</p>
                                  <p className="text-slate-900 font-medium">{userData.username}</p>
                                </div>
                              </div>

                              <div className="flex items-start gap-3">
                                <div className="p-2 bg-white rounded-lg">
                                  <Mail className="w-5 h-5 text-slate-600" />
                                </div>
                                <div>
                                  <p className="text-xs font-semibold text-slate-500 uppercase">Email</p>
                                  <p className="text-slate-900 font-medium">{userData.email}</p>
                                </div>
                              </div>

                              <div className="flex items-start gap-3">
                                <div className="p-2 bg-white rounded-lg">
                                  <Users className="w-5 h-5 text-slate-600" />
                                </div>
                                <div>
                                  <p className="text-xs font-semibold text-slate-500 uppercase">Nombre Completo</p>
                                  <p className="text-slate-900 font-medium">{userData.full_name}</p>
                                </div>
                              </div>

                              <div className="flex items-start gap-3">
                                <div className="p-2 bg-white rounded-lg">
                                  <Shield className="w-5 h-5 text-slate-600" />
                                </div>
                                <div>
                                  <p className="text-xs font-semibold text-slate-500 uppercase">Rol</p>
                                  <p className="text-slate-900 font-medium">{userData.rol_actual?.nombre ?? "—"}</p>
                                </div>
                              </div>

                              <div className="flex items-start gap-3">
                                <div className="p-2 bg-white rounded-lg">
                                  {userData.is_active ? <UserCheck className="w-5 h-5 text-green-600" /> : <UserX className="w-5 h-5 text-red-600" />}
                                </div>
                                <div>
                                  <p className="text-xs font-semibold text-slate-500 uppercase">Estado</p>
                                  <p className={`font-medium ${userData.is_active ? 'text-green-600' : 'text-red-600'}`}>
                                    {userData.is_active ? "Activo" : "Inactivo"}
                                  </p>
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* Actividad reciente */}
                          <div className="bg-gradient-to-br from-slate-50 to-indigo-50 rounded-xl p-6">
                            <div className="flex items-center gap-3 mb-4 pb-3 border-b-2 border-indigo-200">
                              <Activity className="w-5 h-5 text-indigo-600" />
                              <h4 className="font-bold text-lg text-slate-800">Actividad Reciente</h4>
                            </div>

                            {!userLog.length ? (
                              <div className="text-center py-8">
                                <Activity className="w-12 h-12 text-slate-300 mx-auto mb-3" />
                                <p className="text-slate-500">No hay actividad registrada</p>
                              </div>
                            ) : (
                              <ul className="space-y-3">
                                {userLog.map(entry => (
                                  <li key={entry.id} className="bg-white rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow duration-200">
                                    <div className="flex items-start gap-3">
                                      <div className="p-2 bg-indigo-100 rounded-lg">
                                        <Activity className="w-4 h-4 text-indigo-600" />
                                      </div>
                                      <div className="flex-1">
                                        <p className="font-medium text-slate-900">{entry.action}</p>
                                        <p className="text-xs text-slate-500 mt-1 flex items-center gap-2">
                                          <Calendar className="w-3 h-3" />
                                          {entry.date} — IP: {entry.ip}
                                        </p>
                                      </div>
                                    </div>
                                  </li>
                                ))}
                              </ul>
                            )}
                          </div>
                        </div>
                      )}

                      {(mode === "edit" || mode === "new") && (
                        <form onSubmit={handleSubmit} className="space-y-5">
                          {/* Usuario y Email */}
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <label className="block text-sm font-semibold text-slate-700 mb-2">
                                Usuario
                              </label>
                              <input
                                name="username"
                                value={form.username}
                                onChange={handleChange}
                                required
                                className="w-full px-4 py-2.5 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:ring-4 focus:ring-blue-100 outline-none transition-all duration-200"
                              />
                              {errors.username && (
                                <p className="text-red-500 text-sm mt-1">{errors.username}</p>
                              )}
                            </div>
                            <div>
                              <label className="flex items-center gap-2 text-sm font-semibold text-slate-700 mb-2">
                                <Mail className="w-4 h-4" />
                                Email
                              </label>
                              <input
                                name="email"
                                type="email"
                                value={form.email}
                                onChange={handleChange}
                                required
                                className="w-full px-4 py-2.5 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:ring-4 focus:ring-blue-100 outline-none transition-all duration-200"
                              />
                              {errors.email && (
                                <p className="text-red-500 text-sm mt-1">{errors.email}</p>
                              )}
                            </div>
                          </div>

                          {/* Nombres */}
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <label className="block text-sm font-semibold text-slate-700 mb-2">
                                Nombre
                              </label>
                              <input
                                name="first_name"
                                value={form.first_name}
                                onChange={handleChange}
                                className="w-full px-4 py-2.5 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:ring-4 focus:ring-blue-100 outline-none transition-all duration-200"
                              />
                              {errors.first_name && (
                                <p className="text-red-500 text-sm mt-1">{errors.first_name}</p>
                              )}
                            </div>
                            <div>
                              <label className="block text-sm font-semibold text-slate-700 mb-2">
                                Apellido
                              </label>
                              <input
                                name="last_name"
                                value={form.last_name}
                                onChange={handleChange}
                                className="w-full px-4 py-2.5 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:ring-4 focus:ring-blue-100 outline-none transition-all duration-200"
                              />
                              {errors.last_name && (
                                <p className="text-red-500 text-sm mt-1">{errors.last_name}</p>
                              )}
                            </div>
                          </div>

                          {/* Fecha, Sexo y Celular */}
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                              <label className="flex items-center gap-2 text-sm font-semibold text-slate-700 mb-2">
                                <Calendar className="w-4 h-4" />
                                Fecha de Nacimiento
                              </label>
                              <input
                                type="date"
                                name="fecha_de_nacimiento"
                                value={form.fecha_de_nacimiento}
                                onChange={handleChange}
                                max={new Date().toISOString().split('T')[0]}
                                className="w-full px-4 py-2.5 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:ring-4 focus:ring-blue-100 outline-none transition-all duration-200"
                              />
                              {errors.fecha_de_nacimiento && (
                                <p className="text-red-500 text-sm mt-1">{errors.fecha_de_nacimiento}</p>
                              )}
                            </div>
                            <div>
                              <label className="block text-sm font-semibold text-slate-700 mb-2">
                                Sexo
                              </label>
                              <select
                                name="sexo"
                                value={form.sexo}
                                onChange={handleChange}
                                className="w-full px-4 py-2.5 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:ring-4 focus:ring-blue-100 outline-none transition-all duration-200"
                              >
                                <option value="">Seleccionar</option>
                                <option value="M">Masculino</option>
                                <option value="F">Femenino</option>
                                <option value="O">Otro</option>
                              </select>
                              {errors.sexo && (
                                <p className="text-red-500 text-sm mt-1">{errors.sexo}</p>
                              )}
                            </div>
                            <div>
                              <label className="flex items-center gap-2 text-sm font-semibold text-slate-700 mb-2">
                                <Phone className="w-4 h-4" />
                                Celular
                              </label>
                              <input
                                name="celular"
                                type="tel"
                                value={form.celular}
                                onChange={handleChange}
                                placeholder="Ej: +591 70123456"
                                className="w-full px-4 py-2.5 border-2 border-slate-200 rounded-lg focus:border-blue-500 focus:ring-4 focus:ring-blue-100 outline-none transition-all duration-200"
                              />
                              {errors.celular && (
                                <p className="text-red-500 text-sm mt-1">{errors.celular}</p>
                              )}
                            </div>
                          </div>

                          {/* Campos adicionales para nuevo usuario */}
                          {mode === "new" && (
                            <div className="space-y-4 bg-gradient-to-br from-indigo-50 to-blue-50 p-5 rounded-xl border-2 border-indigo-200">
                              <h5 className="font-bold text-slate-800 flex items-center gap-2">
                                <Shield className="w-5 h-5 text-indigo-600" />
                                Configuración de Acceso
                              </h5>

                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                  <label className="flex items-center gap-2 text-sm font-semibold text-slate-700 mb-2">
                                    <Shield className="w-4 h-4" />
                                    Rol del Usuario
                                  </label>
                                  <select
                                    name="rol"
                                    value={form.rol}
                                    onChange={handleChange}
                                    required
                                    className="w-full px-4 py-2.5 border-2 border-slate-200 rounded-lg focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100 outline-none transition-all duration-200"
                                  >
                                    <option value="cliente">Cliente</option>
                                    <option value="empleadonivel2">Empleado Nivel 2</option>
                                    <option value="empleadonivel1">Empleado Nivel 1</option>
                                    <option value="administrador">Administrador</option>
                                  </select>
                                  {errors.rol && (
                                    <p className="text-red-500 text-sm mt-1">{errors.rol}</p>
                                  )}
                                </div>

                                <div>
                                  <label className="block text-sm font-semibold text-slate-700 mb-2">
                                    Contraseña (opcional)
                                  </label>
                                  <input
                                    name="password"
                                    value={form.password}
                                    onChange={handleChange}
                                    type="password"
                                    placeholder="Dejar vacío para autogenerar"
                                    minLength="6"
                                    className="w-full px-4 py-2.5 border-2 border-slate-200 rounded-lg focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100 outline-none transition-all duration-200"
                                  />
                                  {errors.password && (
                                    <p className="text-red-500 text-sm mt-1">{errors.password}</p>
                                  )}
                                  {form.password && form.password.length < 6 && (
                                    <p className="text-amber-600 text-sm mt-1">La contraseña debe tener al menos 6 caracteres</p>
                                  )}
                                </div>
                              </div>
                            </div>
                          )}

                          {/* Errores */}
                          {Object.keys(errors).length > 0 && (
                            <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg">
                              <div className="flex items-start gap-3">
                                <AlertCircle className="w-5 h-5 text-red-500 mt-0.5" />
                                <div className="flex-1">
                                  <h5 className="font-semibold text-red-800 mb-2">Se encontraron errores:</h5>
                                  <ul className="list-disc list-inside space-y-1 text-sm text-red-700">
                                    {Object.entries(errors).map(([key, value]) => (
                                      <li key={key}>
                                        <strong>{key}:</strong> {Array.isArray(value) ? value.join(", ") : value}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              </div>
                            </div>
                          )}

                          {/* Botones de acción */}
                          <div className="flex gap-3 pt-4 border-t-2 border-slate-200">
                            <button
                              disabled={modalLoading}
                              type="submit"
                              className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                              {modalLoading ? (
                                <>
                                  <RefreshCw className="w-5 h-5 animate-spin" />
                                  Guardando...
                                </>
                              ) : (
                                <>
                                  <Save className="w-5 h-5" />
                                  {mode === "edit" ? "Guardar Cambios" : "Crear Usuario"}
                                </>
                              )}
                            </button>
                            <button
                              type="button"
                              onClick={closeModal}
                              className="px-6 py-3 border-2 border-slate-300 hover:bg-slate-50 rounded-xl font-semibold text-slate-700 transition-all duration-200"
                            >
                              Cancelar
                            </button>
                          </div>
                        </form>
                      )}
                    </>
                  )}
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

/* ---------- Helpers paginación ---------- */
function getQueryPage(url) {
  try {
    if (!url) return 1;
    const u = new URL(url);
    return Number(u.searchParams.get("page") || 1);
  } catch (e) { return 1; }
}
function currentPageFromData(data) {
  if (!data) return 1;
  const next = data.next;
  const prev = data.previous;
  if (!prev && !next) return 1;
  if (!prev && next) return 1;
  if (prev && !next) {
    const prevPage = getQueryPage(prev);
    return prevPage + 1;
  }
  return getQueryPage(prev) + 1;
}