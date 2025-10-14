// src/pages/admin/UsersAdminList.jsx
import React, { useEffect, useState, useRef } from "react";
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
 * UsersAdminList - versión responsive y semántica (TailwindCSS)
 * - Mobile: cards list
 * - Desktop (md+): table
 * - Modal accesible (esc, foco, bloqueo scroll)
 */

export default function UsersAdminList() {
  const { results, loading, error, data, goPage, setSearch, remove, activate, deactivate, refresh } = useAdminUsers();
  const [q, setQ] = useState("");

  const [mode, setMode] = useState("list"); // 'list' | 'view' | 'edit' | 'new'
  const [selectedId, setSelectedId] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  // filtros
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    rol: "",
    is_active: "",
    ordering: "-date_joined"
  });

  const [searchTimeout, setSearchTimeout] = useState(null);

  // modal / detalle
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

  // accessibility refs
  const closeModalBtnRef = useRef(null);

  // Scrollbar CSS fallback
  useEffect(() => {
    const style = document.createElement("style");
    style.innerHTML = `
      .custom-scrollbar { scrollbar-width: thin; scrollbar-color: rgba(99,102,241,0.9) rgba(15,23,42,0.06); }
      .custom-scrollbar::-webkit-scrollbar { height: 10px; width: 10px; }
      .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
      .custom-scrollbar::-webkit-scrollbar-thumb { background-color: rgba(99,102,241,0.85); border-radius: 9999px; border: 3px solid rgba(255,255,255,0.06); }
    `;
    document.head.appendChild(style);
    return () => document.head.removeChild(style);
  }, []);

  // cleanup search timeout
  useEffect(() => {
    return () => {
      if (searchTimeout) clearTimeout(searchTimeout);
    };
  }, [searchTimeout]);

  // lock body scroll when modal open
  useEffect(() => {
    if (mode !== "list") {
      document.body.style.overflow = "hidden";
      // focus the close button after small delay
      setTimeout(() => closeModalBtnRef.current?.focus?.(), 50);
    } else {
      document.body.style.overflow = "";
    }
    // Esc to close
    const onKey = (e) => {
      if (e.key === "Escape") closeModal();
    };
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode]);

  // SEARCH & FILTERS
  const handleSearchInputChange = (value) => {
    setQ(value);

    if (searchTimeout) clearTimeout(searchTimeout);

    const timeout = setTimeout(() => {
      const searchParams = { search: value, ...filters };
      Object.keys(searchParams).forEach(k => {
        if (searchParams[k] === "" || searchParams[k] == null) delete searchParams[k];
      });
      setSearch(searchParams);
    }, 500);

    setSearchTimeout(timeout);
  };

  const handleFilterChange = (filterKey, value) => {
    const newFilters = { ...filters, [filterKey]: value };
    setFilters(newFilters);
    const searchParams = { search: q, ...newFilters };
    Object.keys(searchParams).forEach(k => {
      if (searchParams[k] === "" || searchParams[k] == null) delete searchParams[k];
    });
    setSearch(searchParams);
  };

  const clearFilters = () => {
    setQ("");
    setFilters({ rol: "", is_active: "", ordering: "-date_joined" });
    setSearch({});
  };

  const getActiveFiltersCount = () => {
    let count = 0;
    if (q) count++;
    if (filters.rol) count++;
    if (filters.is_active !== "") count++;
    return count;
  };

  // MODAL actions
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

  const loadUserIntoModal = async (id) => {
    setModalLoading(true);
    setUserData(null);
    setUserLog([]);
    setErrors({});
    try {
      const res = await adminGetUser(id);
      setUserData(res.data);
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

  // CRUD actions
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

  const handleToggleActive = async (user) => {
    if (user.id == null) return;
    const verb = user.is_active ? "desactivar" : "activar";
    if (!confirm(`${verb[0].toUpperCase() + verb.slice(1)} usuario ${user.username}?`)) return;
    setActionLoading(true);
    try {
      if (user.is_active) await deactivate(user.id);
      else await activate(user.id);
      alert(`Usuario ${user.is_active ? "desactivado" : "activado"}`);
      await refresh();
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.error || "Error al cambiar estado");
    } finally {
      setActionLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});
    setModalLoading(true);
    try {
      if (mode === "edit" && selectedId) {
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

  // Helpers paginación (mantengo tus helpers)
  function getQueryPage(url) {
    try {
      if (!url) return 1;
      const u = new URL(url);
      return Number(u.searchParams.get("page") || 1);
    } catch (e) { return 1; }
  }
  function currentPageFromData(d) {
    if (!d) return 1;
    const next = d.next;
    const prev = d.previous;
    if (!prev && !next) return 1;
    if (!prev && next) return 1;
    if (prev && !next) {
      const prevPage = getQueryPage(prev);
      return prevPage + 1;
    }
    return getQueryPage(prev) + 1;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-4 sm:p-6">
      <div className="max-w-7xl mx-auto">
        {/* HEADER */}
        <header className="bg-white rounded-2xl shadow-xl p-5 mb-6 border border-slate-200">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-blue-500 to-indigo-600 p-3 rounded-xl shadow-lg">
                <Users className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-2xl sm:text-3xl font-bold text-slate-800">Administración de Usuarios</h1>
                <p className="text-sm text-slate-600">Gestión completa de usuarios del sistema</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={openNew}
                className="flex items-center gap-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white px-3 py-2 rounded-lg shadow hover:brightness-105 transition"
              >
                <Plus className="w-4 h-4" /> Nuevo
              </button>
              <button
                onClick={() => refresh()}
                className="flex items-center gap-2 bg-white border px-3 py-2 rounded-lg shadow-sm hover:shadow transition"
              >
                <RefreshCw className="w-4 h-4" />
                Refrescar
              </button>
            </div>
          </div>
        </header>

        {/* SEARCH + FILTERS */}
        <section className="bg-white rounded-2xl shadow-lg p-4 mb-6 border border-slate-200">
          <form onSubmit={(e) => { e.preventDefault(); const searchParams = { search: q, ...filters }; Object.keys(searchParams).forEach(k=>{ if (searchParams[k]===""||searchParams[k]==null) delete searchParams[k]; }); setSearch(searchParams); }}>
            <div className="flex flex-col md:flex-row md:items-center gap-3">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
                <input
                  value={q}
                  onChange={(e) => handleSearchInputChange(e.target.value)}
                  placeholder="Buscar por nombre, email, username..."
                  className="w-full pl-10 pr-3 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-100 focus:border-blue-400 transition"
                  aria-label="Buscar usuarios"
                />
              </div>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setShowFilters(!showFilters)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg border ${showFilters || getActiveFiltersCount() > 0 ? "bg-blue-50 border-blue-200 text-blue-700" : "bg-white border-slate-200 text-slate-700"}`}
                >
                  <Filter className="w-4 h-4" />
                  <span className="hidden sm:inline">Filtros</span>
                  {getActiveFiltersCount() > 0 && (
                    <span className="ml-2 inline-flex items-center justify-center bg-blue-600 text-white text-xs px-2 py-0.5 rounded-full">{getActiveFiltersCount()}</span>
                  )}
                  {showFilters ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </button>

                {getActiveFiltersCount() > 0 && (
                  <button
                    type="button"
                    onClick={clearFilters}
                    className="flex items-center gap-2 px-3 py-2 rounded-lg border bg-red-50 border-red-200 text-red-700"
                  >
                    <FilterX className="w-4 h-4" />
                    <span className="hidden sm:inline">Limpiar</span>
                  </button>
                )}
              </div>
            </div>

            {/* Advanced filters */}
            {showFilters && (
              <div className="mt-4 border-t pt-4 grid grid-cols-1 md:grid-cols-3 gap-3">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Rol</label>
                  <select value={filters.rol} onChange={(e) => handleFilterChange("rol", e.target.value)} className="w-full px-3 py-2 border rounded-lg">
                    <option value="">Todos los roles</option>
                    <option value="administrador">Administrador</option>
                    <option value="empleadonivel1">Empleado Nivel 1</option>
                    <option value="empleadonivel2">Empleado Nivel 2</option>
                    <option value="cliente">Cliente</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Estado</label>
                  <select value={filters.is_active} onChange={(e) => handleFilterChange("is_active", e.target.value)} className="w-full px-3 py-2 border rounded-lg">
                    <option value="">Todos</option>
                    <option value="true">Activos</option>
                    <option value="false">Inactivos</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Ordenar por</label>
                  <select value={filters.ordering} onChange={(e) => handleFilterChange("ordering", e.target.value)} className="w-full px-3 py-2 border rounded-lg">
                    <option value="-date_joined">Más recientes</option>
                    <option value="date_joined">Más antiguos</option>
                    <option value="username">Usuario A-Z</option>
                    <option value="-username">Usuario Z-A</option>
                  </select>
                </div>
              </div>
            )}
          </form>
        </section>

        {/* FEEDBACK */}
        {loading && (
          <div className="mb-4 p-4 bg-blue-50 border-l-4 border-blue-500 rounded-lg flex items-center gap-3">
            <RefreshCw className="w-5 h-5 text-blue-500 animate-spin" />
            <span className="text-blue-700 font-medium">Cargando usuarios...</span>
          </div>
        )}
        {error && (
          <div className="mb-4 p-4 bg-red-50 border-l-4 border-red-500 rounded-lg flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-500" />
            <span className="text-red-700 font-medium">Error: {JSON.stringify(error)}</span>
          </div>
        )}

        {/* LIST / TABLE */}
        <main className="space-y-6">
          {/* MOBILE: cards list */}
          <section aria-labelledby="users-list-mobile" className="md:hidden">
            <h2 id="users-list-mobile" className="sr-only">Usuarios</h2>
            <ul className="space-y-3 custom-scrollbar">
              {!results?.length && !loading ? (
                <li className="bg-white rounded-lg p-6 text-center text-slate-500 border border-slate-100">
                  <Users className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                  <p className="font-medium">No hay usuarios registrados</p>
                </li>
              ) : results.map(u => (
                <li key={u.id} className="bg-white rounded-lg p-4 shadow-sm border border-slate-100">
                  <article className="flex items-start gap-3">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 rounded-full bg-indigo-100 flex items-center justify-center">
                        <Users className="w-6 h-6 text-indigo-700" />
                      </div>
                    </div>

                    <div className="flex-1">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <p className="font-semibold text-slate-900">{u.username}</p>
                          <p className="text-sm text-slate-600">{(u.first_name || "") + " " + (u.last_name || "")}</p>
                        </div>

                        <div className="text-right">
                          <p className="text-xs text-slate-500">{u.email}</p>
                          <p className="text-xs mt-2">
                            <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold ${u.is_active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
                              {u.is_active ? <UserCheck className="w-3 h-3" /> : <UserX className="w-3 h-3" />}
                              {u.is_active ? "Activo" : "Inactivo"}
                            </span>
                          </p>
                        </div>
                      </div>

                      <div className="mt-3 flex flex-wrap gap-2">
                        <button onClick={() => openView(u.id)} className="px-3 py-1.5 rounded-lg bg-blue-50 text-blue-700 text-sm flex items-center gap-2">
                          <Eye className="w-4 h-4" /> Ver
                        </button>
                        <button onClick={() => openEdit(u.id)} className="px-3 py-1.5 rounded-lg bg-indigo-50 text-indigo-700 text-sm flex items-center gap-2">
                          <Edit2 className="w-4 h-4" /> Editar
                        </button>
                        <button onClick={() => handleToggleActive(u)} disabled={actionLoading} className="px-3 py-1.5 rounded-lg border text-sm">
                          {u.is_active ? <><UserX className="w-4 h-4 inline" /> Desactivar</> : <><UserCheck className="w-4 h-4 inline" /> Activar</>}
                        </button>
                        <button onClick={() => handleDelete(u.id, u.username)} disabled={actionLoading} className="px-3 py-1.5 rounded-lg text-sm text-red-600">
                          <Trash2 className="w-4 h-4 inline" /> Eliminar
                        </button>
                      </div>
                    </div>
                  </article>
                </li>
              ))}
            </ul>
          </section>

          {/* DESKTOP: table */}
          <section aria-labelledby="users-table" className="hidden md:block">
            <h2 id="users-table" className="sr-only">Usuarios</h2>
            <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-slate-200">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-100">
                  <thead className="bg-gradient-to-r from-slate-50 to-slate-100">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">ID</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Usuario</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Nombre</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Email</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Rol</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Estado</th>
                      <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Acciones</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-slate-100">
                    {!results?.length && !loading ? (
                      <tr>
                        <td colSpan="7" className="px-6 py-12 text-center text-slate-500">
                          <Users className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                          <p className="text-lg font-medium">No hay usuarios registrados</p>
                        </td>
                      </tr>
                    ) : results.map(u => (
                      <tr key={u.id} className="hover:bg-slate-50 transition">
                        <td className="px-6 py-4">
                          <div className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-slate-100 text-slate-700 font-semibold text-sm">{u.id}</div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="font-medium text-slate-900">{u.username}</div>
                        </td>
                        <td className="px-6 py-4 text-slate-700">{(u.first_name || "") + " " + (u.last_name || "")}</td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2 text-sm text-slate-600"><Mail className="w-4 h-4" />{u.email}</div>
                        </td>
                        <td className="px-6 py-4">
                          <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-100 text-indigo-700">
                            <Shield className="w-3 h-3" />
                            {u.rol ?? u.rol_actual?.nombre ?? "—"}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          {u.is_active ? (
                            <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-700">
                              <UserCheck className="w-3 h-3" /> Activo
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-red-100 text-red-700">
                              <UserX className="w-3 h-3" /> Inactivo
                            </span>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            <button onClick={() => openView(u.id)} className="px-3 py-1.5 rounded-lg text-sm bg-blue-50 text-blue-700 flex items-center gap-2"><Eye className="w-4 h-4" />Ver</button>
                            <button onClick={() => openEdit(u.id)} className="px-3 py-1.5 rounded-lg text-sm bg-indigo-50 text-indigo-700 flex items-center gap-2"><Edit2 className="w-4 h-4" />Editar</button>
                            <button onClick={() => handleToggleActive(u)} disabled={actionLoading} className="px-3 py-1.5 rounded-lg text-sm border">
                              {u.is_active ? <><UserX className="w-4 h-4 inline" /> Desactivar</> : <><UserCheck className="w-4 h-4 inline" /> Activar</>}
                            </button>
                            <button onClick={() => handleDelete(u.id, u.username)} disabled={actionLoading} className="px-3 py-1.5 rounded-lg text-sm text-red-600"><Trash2 className="w-4 h-4" />Eliminar</button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </section>

          {/* PAGINATION */}
          {data && (
            <section className="mt-2 bg-white rounded-2xl shadow p-4 border border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-3">
              <div className="text-sm text-slate-600">Total de usuarios: <span className="font-semibold text-slate-900">{data.count ?? "—"}</span></div>
              <div className="flex items-center gap-2">
                <button disabled={!data.previous} onClick={() => goPage(Math.max(1, getQueryPage(data.previous) - 1))} className="px-3 py-2 rounded-lg border disabled:opacity-50"> <ChevronLeft className="w-4 h-4" /> Anterior</button>
                <div className="px-4 py-2 bg-gradient-to-r from-blue-500 to-indigo-500 text-white rounded-lg font-semibold">Página {currentPageFromData(data)}</div>
                <button disabled={!data.next} onClick={() => goPage(getQueryPage(data.next) + 1)} className="px-3 py-2 rounded-lg border disabled:opacity-50">Siguiente <ChevronRight className="w-4 h-4" /></button>
              </div>
            </section>
          )}
        </main>

        {/* MODAL */}
        {mode !== "list" && (
          <>
            <div className="fixed inset-0 z-40 bg-black/40" onClick={closeModal} aria-hidden />
            <div className="fixed inset-0 z-50 flex items-start sm:items-center justify-center p-4">
              <div className="w-full max-w-3xl bg-white rounded-2xl shadow-2xl overflow-hidden" role="dialog" aria-modal="true" aria-labelledby="modal-title">
                <header className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
                  <div className="flex items-center gap-3">
                    {mode === "view" && <Eye className="w-5 h-5" />}
                    {mode === "edit" && <Edit2 className="w-5 h-5" />}
                    {mode === "new" && <Plus className="w-5 h-5" />}
                    <h3 id="modal-title" className="text-lg font-semibold">
                      {mode === "view" ? "Ver usuario" : mode === "edit" ? "Editar usuario" : "Nuevo usuario"}
                    </h3>
                  </div>
                  <div>
                    <button ref={closeModalBtnRef} onClick={closeModal} className="p-2 rounded-md hover:bg-white/20">
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                </header>

                <div className="p-5 max-h-[80vh] overflow-y-auto">
                  {modalLoading ? (
                    <div className="flex flex-col items-center justify-center py-12">
                      <RefreshCw className="w-12 h-12 text-blue-500 animate-spin mb-4" />
                      <p className="text-slate-600">Cargando...</p>
                    </div>
                  ) : (
                    <>
                      {/* VIEW */}
                      {mode === "view" && userData && (
                        <section aria-labelledby="user-info">
                          <h4 id="user-info" className="sr-only">Información del usuario</h4>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                            <div className="bg-slate-50 p-4 rounded-lg">
                              <p className="text-xs text-slate-500 uppercase">Usuario</p>
                              <p className="font-medium text-slate-900">{userData.username}</p>
                            </div>
                            <div className="bg-slate-50 p-4 rounded-lg">
                              <p className="text-xs text-slate-500 uppercase">Email</p>
                              <p className="font-medium text-slate-900">{userData.email}</p>
                            </div>
                            <div className="bg-slate-50 p-4 rounded-lg">
                              <p className="text-xs text-slate-500 uppercase">Nombre completo</p>
                              <p className="font-medium text-slate-900">{userData.full_name}</p>
                            </div>
                            <div className="bg-slate-50 p-4 rounded-lg">
                              <p className="text-xs text-slate-500 uppercase">Rol</p>
                              <p className="font-medium text-slate-900">{userData.rol_actual?.nombre ?? "—"}</p>
                            </div>
                          </div>

                          <div className="mb-4">
                            <h5 className="font-semibold text-slate-800 mb-2">Actividad reciente</h5>
                            {!userLog.length ? (
                              <div className="text-center py-8 text-slate-500">
                                <Activity className="w-10 h-10 mx-auto mb-3 text-slate-300" />
                                <p>No hay actividad registrada</p>
                              </div>
                            ) : (
                              <ul className="space-y-3">
                                {userLog.map(entry => (
                                  <li key={entry.id} className="bg-white p-3 rounded-lg shadow-sm border">
                                    <div className="flex items-start gap-3">
                                      <div className="p-2 bg-indigo-50 rounded">
                                        <Activity className="w-4 h-4 text-indigo-600" />
                                      </div>
                                      <div>
                                        <p className="font-medium text-slate-900">{entry.action}</p>
                                        <p className="text-xs text-slate-500 mt-1 flex items-center gap-2"><Calendar className="w-3 h-3" />{entry.date} • IP: {entry.ip}</p>
                                      </div>
                                    </div>
                                  </li>
                                ))}
                              </ul>
                            )}
                          </div>
                        </section>
                      )}

                      {/* FORM (edit/new) */}
                      {(mode === "edit" || mode === "new") && (
                        <form onSubmit={handleSubmit} className="space-y-4">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            <div>
                              <label className="block text-sm font-medium text-slate-700">Usuario</label>
                              <input name="username" value={form.username} onChange={handleChange} required className="w-full px-3 py-2 border rounded-lg" />
                              {errors.username && <p className="text-red-500 text-sm mt-1">{errors.username}</p>}
                            </div>
                            <div>
                              <label className="block text-sm font-medium text-slate-700">Email</label>
                              <input name="email" type="email" value={form.email} onChange={handleChange} required className="w-full px-3 py-2 border rounded-lg" />
                              {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
                            </div>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            <div>
                              <label className="block text-sm font-medium text-slate-700">Nombre</label>
                              <input name="first_name" value={form.first_name} onChange={handleChange} className="w-full px-3 py-2 border rounded-lg" />
                              {errors.first_name && <p className="text-red-500 text-sm mt-1">{errors.first_name}</p>}
                            </div>
                            <div>
                              <label className="block text-sm font-medium text-slate-700">Apellido</label>
                              <input name="last_name" value={form.last_name} onChange={handleChange} className="w-full px-3 py-2 border rounded-lg" />
                              {errors.last_name && <p className="text-red-500 text-sm mt-1">{errors.last_name}</p>}
                            </div>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                            <div>
                              <label className="flex items-center gap-2 text-sm font-medium text-slate-700"> <Calendar className="w-4 h-4" /> Fecha de Nac.</label>
                              <input type="date" name="fecha_de_nacimiento" value={form.fecha_de_nacimiento} onChange={handleChange} max={new Date().toISOString().split('T')[0]} className="w-full px-3 py-2 border rounded-lg" />
                              {errors.fecha_de_nacimiento && <p className="text-red-500 text-sm mt-1">{errors.fecha_de_nacimiento}</p>}
                            </div>
                            <div>
                              <label className="block text-sm font-medium text-slate-700">Sexo</label>
                              <select name="sexo" value={form.sexo} onChange={handleChange} className="w-full px-3 py-2 border rounded-lg">
                                <option value="">Seleccionar</option>
                                <option value="M">Masculino</option>
                                <option value="F">Femenino</option>
                                <option value="O">Otro</option>
                              </select>
                              {errors.sexo && <p className="text-red-500 text-sm mt-1">{errors.sexo}</p>}
                            </div>
                            <div>
                              <label className="flex items-center gap-2 text-sm font-medium text-slate-700"><Phone className="w-4 h-4" /> Celular</label>
                              <input name="celular" type="tel" value={form.celular} onChange={handleChange} placeholder="+591 7xxxxxxx" className="w-full px-3 py-2 border rounded-lg" />
                              {errors.celular && <p className="text-red-500 text-sm mt-1">{errors.celular}</p>}
                            </div>
                          </div>

                          {mode === "new" && (
                            <div className="p-3 bg-indigo-50 rounded-lg border border-indigo-100">
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                <div>
                                  <label className="block text-sm font-medium text-slate-700">Rol</label>
                                  <select name="rol" value={form.rol} onChange={handleChange} className="w-full px-3 py-2 border rounded-lg">
                                    <option value="cliente">Cliente</option>
                                    <option value="empleadonivel2">Empleado Nivel 2</option>
                                    <option value="empleadonivel1">Empleado Nivel 1</option>
                                    <option value="administrador">Administrador</option>
                                  </select>
                                </div>
                                <div>
                                  <label className="block text-sm font-medium text-slate-700">Contraseña (opcional)</label>
                                  <input name="password" type="password" value={form.password} onChange={handleChange} placeholder="Dejar vacío para autogenerar" className="w-full px-3 py-2 border rounded-lg" minLength={6} />
                                  {form.password && form.password.length < 6 && <p className="text-amber-600 text-sm mt-1">La contraseña debe tener al menos 6 caracteres</p>}
                                </div>
                              </div>
                            </div>
                          )}

                          {Object.keys(errors).length > 0 && (
                            <div className="bg-red-50 border-l-4 border-red-500 p-3 rounded">
                              <div className="flex items-start gap-3">
                                <AlertCircle className="w-5 h-5 text-red-500 mt-1" />
                                <div>
                                  <p className="font-semibold text-red-800">Se encontraron errores</p>
                                  <ul className="text-sm text-red-700 list-disc list-inside mt-2">
                                    {Object.entries(errors).map(([k, v]) => (
                                      <li key={k}><strong>{k}:</strong> {Array.isArray(v) ? v.join(", ") : v}</li>
                                    ))}
                                  </ul>
                                </div>
                              </div>
                            </div>
                          )}

                          <div className="flex items-center gap-3 mt-2">
                            <button type="submit" disabled={modalLoading} className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-blue-500 to-indigo-600 text-white font-semibold">
                              {modalLoading ? <><RefreshCw className="w-4 h-4 animate-spin" /> Guardando...</> : <><Save className="w-4 h-4" /> {mode === "edit" ? "Guardar cambios" : "Crear usuario"}</>}
                            </button>
                            <button type="button" onClick={closeModal} className="px-4 py-2 rounded-lg border">Cancelar</button>
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
