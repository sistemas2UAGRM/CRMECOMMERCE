// src/modulos/empleados/Empleados.jsx
import React, { useEffect, useState } from "react";
import {
    PlusCircle, Edit, Trash2, Search as SearchIcon,
    UserCheck, Eye, X, Mail, Phone, Calendar,
    Shield, BadgeCheck
} from "lucide-react";
import api from '../../services/api';
import { toast } from 'react-hot-toast';

// Estado inicial del formulario para poder resetearlo fácilmente
const INITIAL_FORM_STATE = {
    username: "",
    email: "",
    first_name: "",
    last_name: "",
    celular: "",
    fecha_de_nacimiento: "",
    sexo: "M",
    password: "",
    confirmPassword: "",
    is_active: true,
    groups: [], // Para asignar roles
};

// Opciones para el campo sexo
const SEXO_OPTIONS = [
    { value: "M", label: "Masculino" },
    { value: "F", label: "Femenino" },
    { value: "O", label: "Otro" },
];

// Mapeo de roles para mostrar nombres más amigables
const ROLE_DISPLAY = {
    'administrador': { name: 'Administrador', color: 'bg-red-100 text-red-800' },
    'empleadonivel1': { name: 'Supervisor', color: 'bg-yellow-100 text-yellow-800' },
    'empleadonivel2': { name: 'Vendedor', color: 'bg-green-100 text-green-800' },
    'cliente': { name: 'Cliente', color: 'bg-blue-100 text-blue-800' },
    'empleado': { name: 'Empleado', color: 'bg-purple-100 text-purple-800' },
};

// Roles permitidos en el módulo de empleados
const EMPLOYEE_ROLES = ['administrador', 'empleado'];

export default function Empleados() {
    const [employees, setEmployees] = useState([]);
    const [roles, setRoles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [pageInfo, setPageInfo] = useState({ next: null, previous: null, count: 0 });
    const [page, setPage] = useState(1);
    const [query, setQuery] = useState("");
    const [statusFilter, setStatusFilter] = useState("all"); // "all", "active", "inactive"
    const [roleFilter, setRoleFilter] = useState(""); // filtro por rol específico

    const [showFormModal, setShowFormModal] = useState(false);
    const [showDetailsModal, setShowDetailsModal] = useState(false);
    const [formMode, setFormMode] = useState("create"); // 'create' | 'edit'
    const [currentEmployee, setCurrentEmployee] = useState(null);
    const [formState, setFormState] = useState(INITIAL_FORM_STATE);
    const [formError, setFormError] = useState(null);

    // Función para obtener los empleados de la API
    const fetchEmployees = async (currentPage = 1, searchQuery = "", statusFilterParam = statusFilter, roleFilterParam = roleFilter) => {
        setLoading(true);
        setFormError(null);
        try {
            const params = {
                page: currentPage,
                search: searchQuery
            };

            // Aplicar filtro de estado correctamente
            if (statusFilterParam === "active") {
                params.active_only = "true";
            } else if (statusFilterParam === "inactive") {
                params.active_only = "false";
            }
            // Si es "all", no enviamos el parámetro active_only para mostrar todos

            console.log("Filtros aplicados:", { statusFilterParam, roleFilterParam, params });

            const { data } = await api.get("/users/search/employees/", { params });

            let results = data.results || [];
            console.log("Empleados recibidos del backend:", results.length, results);

            // Aplicar filtro por rol en el frontend si es necesario
            if (roleFilterParam && roleFilterParam !== "") {
                const originalCount = results.length;
                results = results.filter(employee =>
                    employee.groups?.some(group => group.name === roleFilterParam)
                );
                console.log(`Filtro de rol aplicado: ${originalCount} -> ${results.length} empleados`);
            }

            setEmployees(results);
            setPageInfo({
                next: data.next,
                previous: data.previous,
                count: data.count || 0,
                num_pages: data.num_pages || 1
            });
            setPage(currentPage);
        } catch (err) {
            console.error("Error al cargar empleados:", err);
            if (err.response?.status === 403) {
                setFormError("No tienes permisos para ver la lista de empleados.");
                toast.error("No tienes permisos para ver la lista de empleados.");
            } else {
                setFormError("Error al cargar empleados.");
                toast.error("Error al cargar empleados.");
            }
        } finally {
            setLoading(false);
        }
    };

    // Función para obtener los roles disponibles
    const fetchRoles = async () => {
        try {
            const { data } = await api.get("/users/search/roles/");
            setRoles(data.roles || []);
        } catch (err) {
            console.error("Error al cargar roles:", err);
            toast.error("Error al cargar roles.");
        }
    };

    // Carga inicial de empleados y roles
    useEffect(() => {
        fetchEmployees(1, "");
        fetchRoles();
    }, []);

    // Efecto para aplicar filtros automáticamente
    useEffect(() => {
        const timeoutId = setTimeout(() => {
            setPage(1);
            fetchEmployees(1, query, statusFilter, roleFilter);
        }, 300); // Debounce de 300ms

        return () => clearTimeout(timeoutId);
    }, [statusFilter, roleFilter]);

    // Handler para la búsqueda y filtros
    const handleSearchSubmit = (e) => {
        if (e) e.preventDefault();
        setPage(1);
        fetchEmployees(1, query, statusFilter, roleFilter);
    };

    // Handler para cambio de filtros
    const handleFilterChange = () => {
        setPage(1);
        fetchEmployees(1, query, statusFilter, roleFilter);
    };

    // Resetea el formulario y cierra el modal
    const resetFormAndClose = () => {
        setFormState(INITIAL_FORM_STATE);
        setCurrentEmployee(null);
        setFormMode("create");
        setShowFormModal(false);
        setFormError(null);
    };

    // Abre el modal para crear un nuevo empleado
    const openCreateModal = () => {
        resetFormAndClose();
        setFormMode("create");
        setShowFormModal(true);
    };

    // Abre el modal para editar un empleado existente
    const openEditModal = (employee) => {
        setFormState({
            username: employee.username || "",
            email: employee.email || "",
            first_name: employee.first_name || "",
            last_name: employee.last_name || "",
            celular: employee.celular || "",
            fecha_de_nacimiento: employee.fecha_de_nacimiento || "",
            sexo: employee.sexo || "M",
            password: "",
            confirmPassword: "",
            is_active: employee.is_active ?? true,
            groups: employee.groups?.map(group => group.id) || [],
        });
        setCurrentEmployee(employee);
        setFormMode("edit");
        setShowFormModal(true);
    };

    // Abre el modal de detalles del empleado
    const openDetailsModal = (employee) => {
        setCurrentEmployee(employee);
        setShowDetailsModal(true);
    };

    // Elimina un empleado
    const handleDelete = async (employeeId) => {
        if (!window.confirm("¿Estás seguro de que quieres eliminar este empleado?")) return;

        try {
            await api.delete(`/users/admin/${employeeId}/`);
            toast.success("Empleado eliminado.");
            fetchEmployees(page, query);
        } catch (err) {
            console.error("Error al eliminar empleado:", err);
            if (err.response?.status === 403) {
                toast.error("No tienes permisos para eliminar empleados.");
            } else {
                toast.error("Error al eliminar el empleado.");
            }
        }
    };

    // Maneja los cambios en los inputs del formulario
    const handleFormChange = (e) => {
        const { name, value, type, checked } = e.target;
        if (type === 'checkbox' && name === 'is_active') {
            setFormState(prev => ({ ...prev, [name]: checked }));
        } else if (name === 'role') {
            // Manejo del dropdown de rol - un solo rol
            setFormState(prev => ({
                ...prev,
                groups: value ? [parseInt(value)] : []
            }));
        } else {
            setFormState(prev => ({ ...prev, [name]: value }));
        }
    };

    // Envía el formulario (crear o editar)
    const handleFormSubmit = async (e) => {
        e.preventDefault();
        setFormError(null);

        // Validaciones básicas
        if (formState.groups.length === 0) {
            setFormError("Debe seleccionar un rol para el empleado.");
            return;
        }

        if (formMode === "create" && formState.password !== formState.confirmPassword) {
            setFormError("Las contraseñas no coinciden.");
            return;
        }

        if (formMode === "create" && formState.password.length < 6) {
            setFormError("La contraseña debe tener al menos 6 caracteres.");
            return;
        }

        const isCreating = formMode === "create";
        const url = isCreating ? "/users/admin-register/" : `/users/admin/${currentEmployee.id}/`;
        const method = isCreating ? 'post' : 'patch';

        // Preparar datos para enviar
        const dataPayload = { ...formState };
        delete dataPayload.confirmPassword; // No enviar confirmación de contraseña

        // Convertir groups (IDs) a rol (nombre del rol) para el backend
        if (dataPayload.groups && dataPayload.groups.length > 0) {
            const roleId = dataPayload.groups[0];
            const role = roles.find(r => r.id === roleId);
            if (role) {
                dataPayload.rol = role.name;
            }
        }
        delete dataPayload.groups; // No enviar groups, solo rol

        // Si es edición y no se cambió la contraseña, no enviarla
        if (!isCreating && !dataPayload.password) {
            delete dataPayload.password;
        }

        try {
            const response = await api[method](url, dataPayload);
            toast.success(`Empleado ${isCreating ? "creado" : "actualizado"} con éxito.`);
            resetFormAndClose();
            fetchEmployees(isCreating ? 1 : page, query);
        } catch (err) {
            console.error("Error submitting form:", err.response?.data || err.message);

            if (err.response?.status === 403) {
                setFormError("No tienes permisos para realizar esta acción.");
                toast.error("No tienes permisos para realizar esta acción.");
            } else {
                const apiErrors = err.response?.data;
                if (typeof apiErrors === 'object' && apiErrors !== null) {
                    const errorMessages = Object.entries(apiErrors)
                        .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
                        .join(' | ');
                    setFormError(`Error: ${errorMessages}`);
                } else {
                    setFormError("Error al guardar el empleado. Revisa los datos.");
                }
                toast.error("Error al guardar el empleado.");
            }
        }
    };

    // Función para formatear fecha
    const formatDate = (dateString) => {
        if (!dateString) return "No especificado";
        return new Date(dateString).toLocaleDateString('es-ES');
    };

    // Función para obtener los roles del empleado
    const getEmployeeRoles = (employee) => {
        if (!employee.groups || employee.groups.length === 0) {
            return [{ name: 'Sin rol', color: 'bg-gray-100 text-gray-800' }];
        }
        return employee.groups.map(group =>
            ROLE_DISPLAY[group.name] || { name: group.name, color: 'bg-gray-100 text-gray-800' }
        );
    };

    return (
        <div className="p-4 space-y-6">
            {/* Cabecera del Módulo */}
            <div className="space-y-4">
                <div className="flex items-center justify-between">
                    <h2 className="text-2xl font-bold text-gray-800">Gestión de Empleados</h2>
                    <button
                        onClick={openCreateModal}
                        className="inline-flex items-center gap-2 rounded-md bg-[#f0a831] px-4 py-2 text-sm font-semibold text-white shadow-md hover:bg-opacity-90 transition"
                    >
                        <PlusCircle size={18} /> Nuevo Empleado
                    </button>
                </div>

                {/* Filtros y Búsqueda */}
                <div className="bg-white p-4 rounded-lg shadow-sm border">
                    <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-end">
                        {/* Búsqueda */}
                        <div className="flex-1">
                            <label className="block text-sm font-medium text-gray-700 mb-1">Buscar empleados</label>
                            <form onSubmit={handleSearchSubmit} className="relative">
                                <input
                                    value={query}
                                    onChange={(e) => setQuery(e.target.value)}
                                    placeholder="Nombre, apellido, email, usuario..."
                                    className="w-full rounded-md border border-gray-300 px-4 py-2 pl-10 shadow-sm focus:outline-none focus:ring-2 focus:ring-[#2e7e8b] focus:border-[#2e7e8b]"
                                />
                                <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                            </form>
                        </div>

                        {/* Filtro por Estado */}
                        <div className="min-w-[150px]">
                            <label className="block text-sm font-medium text-gray-700 mb-1">Estado</label>
                            <select
                                value={statusFilter}
                                onChange={(e) => {
                                    console.log("Cambiando filtro de estado a:", e.target.value);
                                    setStatusFilter(e.target.value);
                                }}
                                className="w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-[#2e7e8b] focus:border-[#2e7e8b]"
                            >
                                <option value="all">Todos</option>
                                <option value="active">Solo Activos</option>
                                <option value="inactive">Solo Inactivos</option>
                            </select>
                        </div>

                        {/* Filtro por Rol */}
                        <div className="min-w-[150px]">
                            <label className="block text-sm font-medium text-gray-700 mb-1">Rol</label>
                            <select
                                value={roleFilter}
                                onChange={(e) => {
                                    console.log("Cambiando filtro de rol a:", e.target.value);
                                    setRoleFilter(e.target.value);
                                }}
                                className="w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-[#2e7e8b] focus:border-[#2e7e8b]"
                            >
                                <option value="">Todos los roles</option>
                                {roles
                                    .filter(role => EMPLOYEE_ROLES.includes(role.name))
                                    .map(role => (
                                        <option key={role.id} value={role.name}>
                                            {ROLE_DISPLAY[role.name]?.name || role.name}
                                        </option>
                                    ))}
                            </select>
                        </div>

                        {/* Botón de búsqueda */}
                        <button
                            onClick={handleSearchSubmit}
                            className="inline-flex items-center gap-2 rounded-md bg-[#2e7e8b] px-4 py-2 text-sm font-semibold text-white shadow-md hover:bg-[#256a76] transition"
                        >
                            <SearchIcon size={16} /> Buscar
                        </button>
                    </div>
                </div>
            </div>

            {/* Tabla de Empleados */}
            <div className="bg-white rounded-lg shadow overflow-x-auto">
                <table className="w-full table-auto">
                    <thead className="bg-gray-50 text-left text-gray-600 uppercase text-sm">
                        <tr>
                            <th className="px-6 py-3">#</th>
                            <th className="px-6 py-3">Empleado</th>
                            <th className="px-6 py-3">Email</th>
                            <th className="px-6 py-3">Teléfono</th>
                            <th className="px-6 py-3">Roles</th>
                            <th className="px-6 py-3">Estado</th>
                            <th className="px-6 py-3">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                        {loading ? (
                            <tr>
                                <td colSpan="7" className="px-6 py-8 text-center text-gray-500">
                                    Cargando empleados...
                                </td>
                            </tr>
                        ) : employees.length === 0 ? (
                            <tr>
                                <td colSpan="7" className="px-6 py-8 text-center text-gray-500">
                                    No se encontraron empleados
                                </td>
                            </tr>
                        ) : (
                            employees.map((employee, index) => (
                                <tr key={employee.id} className="hover:bg-gray-50">
                                    <td className="px-6 py-4 text-sm text-gray-900">
                                        {(page - 1) * 20 + index + 1}
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex items-center space-x-3">
                                            <div className="flex-shrink-0">
                                                <div className="h-10 w-10 rounded-full bg-[#2e7e8b] flex items-center justify-center">
                                                    <UserCheck className="h-5 w-5 text-white" />
                                                </div>
                                            </div>
                                            <div>
                                                <p className="text-sm font-medium text-gray-900">
                                                    {employee.first_name} {employee.last_name}
                                                </p>
                                                <p className="text-sm text-gray-500">@{employee.username}</p>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex items-center text-sm text-gray-900">
                                            <Mail className="h-4 w-4 mr-2 text-gray-400" />
                                            {employee.email}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex items-center text-sm text-gray-900">
                                            <Phone className="h-4 w-4 mr-2 text-gray-400" />
                                            {employee.celular || "No especificado"}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex flex-wrap gap-1">
                                            {getEmployeeRoles(employee).map((role, idx) => (
                                                <span
                                                    key={idx}
                                                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${role.color}`}
                                                >
                                                    <Shield className="h-3 w-3 mr-1" />
                                                    {role.name}
                                                </span>
                                            ))}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${employee.is_active
                                            ? 'bg-green-100 text-green-800'
                                            : 'bg-red-100 text-red-800'
                                            }`}>
                                            <BadgeCheck className="h-3 w-3 mr-1" />
                                            {employee.is_active ? 'Activo' : 'Inactivo'}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-right text-sm font-medium space-x-2">
                                        <button
                                            onClick={() => openDetailsModal(employee)}
                                            className="text-[#2e7e8b] hover:text-[#1e5a64] transition-colors"
                                            title="Ver detalles"
                                        >
                                            <Eye size={18} />
                                        </button>
                                        <button
                                            onClick={() => openEditModal(employee)}
                                            className="text-blue-600 hover:text-blue-800 transition-colors"
                                            title="Editar empleado"
                                        >
                                            <Edit size={18} />
                                        </button>
                                        <button
                                            onClick={() => handleDelete(employee.id)}
                                            className="text-red-600 hover:text-red-800 transition-colors"
                                            title="Eliminar empleado"
                                        >
                                            <Trash2 size={18} />
                                        </button>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            {/* Paginación */}
            {pageInfo.count > 0 && (
                <div className="flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3 sm:px-6 rounded-b-lg">
                    <div className="flex flex-1 justify-between sm:hidden">
                        <button
                            onClick={() => page > 1 && fetchEmployees(page - 1, query)}
                            disabled={page <= 1}
                            className="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                        >
                            Anterior
                        </button>
                        <button
                            onClick={() => pageInfo.next && fetchEmployees(page + 1, query)}
                            disabled={!pageInfo.next || page >= (pageInfo.num_pages || Math.ceil(pageInfo.count / 20))}
                            className="relative ml-3 inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                        >
                            Siguiente
                        </button>
                    </div>
                    <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
                        <div>
                            <p className="text-sm text-gray-700">
                                Mostrando página <span className="font-medium">{page}</span> de{' '}
                                <span className="font-medium">{pageInfo.num_pages || Math.ceil(pageInfo.count / 20)}</span> |{' '}
                                <span className="font-medium">{pageInfo.count}</span> empleados en total
                            </p>
                        </div>
                        <div className="space-x-2">
                            <button
                                onClick={() => page > 1 && fetchEmployees(page - 1, query)}
                                disabled={page <= 1}
                                className="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-3 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                            >
                                Anterior
                            </button>
                            <button
                                onClick={() => pageInfo.next && fetchEmployees(page + 1, query)}
                                disabled={!pageInfo.next || page >= (pageInfo.num_pages || Math.ceil(pageInfo.count / 20))}
                                className="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-3 py-2 text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                            >
                                Siguiente
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Modal de Formulario */}
            {showFormModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
                    <div className="w-full max-w-3xl rounded-lg bg-white p-6 shadow-2xl animate-fade-in-down max-h-[90vh] overflow-y-auto">
                        <div className="flex items-center justify-between pb-3 border-b">
                            <h3 className="text-xl font-semibold text-gray-800">
                                {formMode === "create" ? "Crear Nuevo Empleado" : `Editar: ${currentEmployee?.first_name} ${currentEmployee?.last_name}`}
                            </h3>
                            <button onClick={resetFormAndClose} className="p-1 rounded-full hover:bg-gray-100">
                                <X size={20} className="text-gray-600" />
                            </button>
                        </div>

                        <form className="mt-4" onSubmit={handleFormSubmit}>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {/* Username */}
                                <div>
                                    <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">Nombre de usuario *</label>
                                    <input
                                        id="username"
                                        name="username"
                                        value={formState.username}
                                        onChange={handleFormChange}
                                        placeholder="nombre_usuario"
                                        className="w-full rounded border-gray-300 px-3 py-2 shadow-sm focus:ring-[#2e7e8b] focus:border-[#2e7e8b]"
                                        required
                                    />
                                </div>

                                {/* Email */}
                                <div>
                                    <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">Email *</label>
                                    <input
                                        id="email"
                                        name="email"
                                        type="email"
                                        value={formState.email}
                                        onChange={handleFormChange}
                                        placeholder="empleado@empresa.com"
                                        className="w-full rounded border-gray-300 px-3 py-2 shadow-sm focus:ring-[#2e7e8b] focus:border-[#2e7e8b]"
                                        required
                                    />
                                </div>

                                {/* Nombre */}
                                <div>
                                    <label htmlFor="first_name" className="block text-sm font-medium text-gray-700 mb-1">Nombre *</label>
                                    <input
                                        id="first_name"
                                        name="first_name"
                                        value={formState.first_name}
                                        onChange={handleFormChange}
                                        placeholder="Juan"
                                        className="w-full rounded border-gray-300 px-3 py-2 shadow-sm focus:ring-[#2e7e8b] focus:border-[#2e7e8b]"
                                        required
                                    />
                                </div>

                                {/* Apellido */}
                                <div>
                                    <label htmlFor="last_name" className="block text-sm font-medium text-gray-700 mb-1">Apellido *</label>
                                    <input
                                        id="last_name"
                                        name="last_name"
                                        value={formState.last_name}
                                        onChange={handleFormChange}
                                        placeholder="Pérez"
                                        className="w-full rounded border-gray-300 px-3 py-2 shadow-sm focus:ring-[#2e7e8b] focus:border-[#2e7e8b]"
                                        required
                                    />
                                </div>

                                {/* Teléfono */}
                                <div>
                                    <label htmlFor="celular" className="block text-sm font-medium text-gray-700 mb-1">Teléfono</label>
                                    <input
                                        id="celular"
                                        name="celular"
                                        type="tel"
                                        value={formState.celular}
                                        onChange={handleFormChange}
                                        placeholder="+591 70123456"
                                        className="w-full rounded border-gray-300 px-3 py-2 shadow-sm focus:ring-[#2e7e8b] focus:border-[#2e7e8b]"
                                    />
                                </div>

                                {/* Fecha de nacimiento */}
                                <div>
                                    <label htmlFor="fecha_de_nacimiento" className="block text-sm font-medium text-gray-700 mb-1">Fecha de nacimiento</label>
                                    <input
                                        id="fecha_de_nacimiento"
                                        name="fecha_de_nacimiento"
                                        type="date"
                                        value={formState.fecha_de_nacimiento}
                                        onChange={handleFormChange}
                                        className="w-full rounded border-gray-300 px-3 py-2 shadow-sm focus:ring-[#2e7e8b] focus:border-[#2e7e8b]"
                                    />
                                </div>

                                {/* Sexo */}
                                <div>
                                    <label htmlFor="sexo" className="block text-sm font-medium text-gray-700 mb-1">Sexo</label>
                                    <select
                                        id="sexo"
                                        name="sexo"
                                        value={formState.sexo}
                                        onChange={handleFormChange}
                                        className="w-full rounded border-gray-300 px-3 py-2 shadow-sm focus:ring-[#2e7e8b] focus:border-[#2e7e8b]"
                                    >
                                        {SEXO_OPTIONS.map(option => (
                                            <option key={option.value} value={option.value}>
                                                {option.label}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                {/* Rol del empleado */}
                                <div>
                                    <label htmlFor="role" className="block text-sm font-medium text-gray-700 mb-2">Rol del empleado *</label>
                                    <select
                                        id="role"
                                        name="role"
                                        value={formState.groups[0] || ''}
                                        onChange={handleFormChange}
                                        className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-[#2e7e8b] focus:border-transparent"
                                        required
                                    >
                                        <option value="">Selecciona un rol</option>
                                        {roles
                                            .filter(role => EMPLOYEE_ROLES.includes(role.name))
                                            .map(role => (
                                                <option key={role.id} value={role.id}>
                                                    {ROLE_DISPLAY[role.name]?.name || role.name}
                                                </option>
                                            ))}
                                    </select>
                                    {formState.groups.length === 0 && (
                                        <p className="text-xs text-red-500 mt-1">* Debe seleccionar un rol</p>
                                    )}
                                    {formState.groups.length > 0 && (
                                        <p className="text-xs text-green-600 mt-1">
                                            ✓ Rol seleccionado: {
                                                (() => {
                                                    const roleId = formState.groups[0];
                                                    const role = roles.find(r => r.id === roleId);
                                                    return role ? (ROLE_DISPLAY[role.name]?.name || role.name) : 'Rol no encontrado';
                                                })()
                                            }
                                        </p>
                                    )}
                                </div>

                                {/* Contraseñas para crear nuevo empleado */}
                                {formMode === "create" && (
                                    <>
                                        <div>
                                            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">Contraseña *</label>
                                            <input
                                                id="password"
                                                name="password"
                                                type="password"
                                                value={formState.password}
                                                onChange={handleFormChange}
                                                placeholder="Mínimo 6 caracteres"
                                                className="w-full rounded border-gray-300 px-3 py-2 shadow-sm focus:ring-[#2e7e8b] focus:border-[#2e7e8b]"
                                                required
                                            />
                                        </div>

                                        <div>
                                            <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">Confirmar contraseña *</label>
                                            <input
                                                id="confirmPassword"
                                                name="confirmPassword"
                                                type="password"
                                                value={formState.confirmPassword}
                                                onChange={handleFormChange}
                                                placeholder="Repite la contraseña"
                                                className="w-full rounded border-gray-300 px-3 py-2 shadow-sm focus:ring-[#2e7e8b] focus:border-[#2e7e8b]"
                                                required
                                            />
                                        </div>
                                    </>
                                )}

                                {/* Nueva contraseña para edición */}
                                {formMode === "edit" && (
                                    <div className="md:col-span-2">
                                        <label htmlFor="password_edit" className="block text-sm font-medium text-gray-700 mb-1">Nueva contraseña (dejar vacío para no cambiar)</label>
                                        <input
                                            id="password_edit"
                                            name="password"
                                            type="password"
                                            value={formState.password}
                                            onChange={handleFormChange}
                                            placeholder="Nueva contraseña (opcional)"
                                            className="w-full rounded border-gray-300 px-3 py-2 shadow-sm focus:ring-[#2e7e8b] focus:border-[#2e7e8b]"
                                        />
                                    </div>
                                )}

                                {/* Estado activo */}
                                <div className="md:col-span-2 flex items-center gap-2">
                                    <input
                                        id="is_active"
                                        name="is_active"
                                        type="checkbox"
                                        checked={formState.is_active}
                                        onChange={handleFormChange}
                                        className="h-4 w-4 rounded border-gray-300 text-[#2e7e8b] focus:ring-[#2e7e8b]"
                                    />
                                    <label htmlFor="is_active" className="text-sm font-medium text-gray-700">Empleado activo</label>
                                </div>
                            </div>

                            {formError && (
                                <div className="mt-3 text-sm text-red-600 bg-red-50 p-3 rounded-md border border-red-200">
                                    {formError}
                                </div>
                            )}

                            <div className="flex items-center justify-end gap-3 pt-4 mt-4 border-t">
                                <button
                                    type="button"
                                    onClick={resetFormAndClose}
                                    className="px-4 py-2 rounded-md border bg-gray-50 text-gray-700 font-medium hover:bg-gray-100"
                                >
                                    Cancelar
                                </button>
                                <button
                                    type="submit"
                                    className="px-4 py-2 rounded-md bg-[#2e7e8b] text-white font-semibold hover:bg-[#256a76]"
                                >
                                    {formMode === "create" ? "Crear Empleado" : "Guardar Cambios"}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Modal de Detalles */}
            {showDetailsModal && currentEmployee && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
                    <div className="w-full max-w-lg rounded-lg bg-white p-6 shadow-2xl animate-fade-in-down">
                        <div className="flex items-center justify-between pb-3 border-b">
                            <h3 className="text-xl font-semibold text-gray-800">
                                Detalles del Empleado
                            </h3>
                            <button onClick={() => setShowDetailsModal(false)} className="p-1 rounded-full hover:bg-gray-100">
                                <X size={20} className="text-gray-600" />
                            </button>
                        </div>

                        <div className="mt-4 space-y-4">
                            {/* Avatar y nombre */}
                            <div className="flex items-center space-x-4 bg-gray-50 p-4 rounded-lg">
                                <div className="h-16 w-16 rounded-full bg-[#2e7e8b] flex items-center justify-center">
                                    <UserCheck className="h-8 w-8 text-white" />
                                </div>
                                <div>
                                    <h4 className="text-xl font-semibold text-gray-900">
                                        {currentEmployee.first_name} {currentEmployee.last_name}
                                    </h4>
                                    <p className="text-gray-500">@{currentEmployee.username}</p>
                                </div>
                            </div>

                            {/* Información personal */}
                            <div className="grid grid-cols-1 gap-3">
                                <div className="flex items-center justify-between border-b border-gray-100 pb-2">
                                    <label className="text-sm font-medium text-gray-500 flex items-center">
                                        <Mail className="h-4 w-4 mr-2" />
                                        Email
                                    </label>
                                    <p className="text-sm text-gray-900">{currentEmployee.email}</p>
                                </div>

                                <div className="flex items-center justify-between border-b border-gray-100 pb-2">
                                    <label className="text-sm font-medium text-gray-500 flex items-center">
                                        <Phone className="h-4 w-4 mr-2" />
                                        Teléfono
                                    </label>
                                    <p className="text-sm text-gray-900">
                                        {currentEmployee.celular || "No especificado"}
                                    </p>
                                </div>

                                <div className="flex items-center justify-between border-b border-gray-100 pb-2">
                                    <label className="text-sm font-medium text-gray-500 flex items-center">
                                        <Calendar className="h-4 w-4 mr-2" />
                                        F. Nacimiento
                                    </label>
                                    <p className="text-sm text-gray-900">
                                        {formatDate(currentEmployee.fecha_de_nacimiento)}
                                    </p>
                                </div>

                                <div className="flex items-center justify-between border-b border-gray-100 pb-2">
                                    <label className="text-sm font-medium text-gray-500">Sexo</label>
                                    <p className="text-sm text-gray-900">
                                        {SEXO_OPTIONS.find(opt => opt.value === currentEmployee.sexo)?.label || "No especificado"}
                                    </p>
                                </div>

                                <div className="border-b border-gray-100 pb-2">
                                    <label className="text-sm font-medium text-gray-500 mb-2 block">Roles</label>
                                    <div className="flex flex-wrap gap-2">
                                        {getEmployeeRoles(currentEmployee).map((role, idx) => (
                                            <span
                                                key={idx}
                                                className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${role.color}`}
                                            >
                                                <Shield className="h-3 w-3 mr-1" />
                                                {role.name}
                                            </span>
                                        ))}
                                    </div>
                                </div>

                                <div className="flex items-center justify-between border-b border-gray-100 pb-2">
                                    <label className="text-sm font-medium text-gray-500">Estado</label>
                                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${currentEmployee.is_active
                                        ? 'bg-green-100 text-green-800'
                                        : 'bg-red-100 text-red-800'
                                        }`}>
                                        <BadgeCheck className="h-3 w-3 mr-1" />
                                        {currentEmployee.is_active ? 'Activo' : 'Inactivo'}
                                    </span>
                                </div>

                                <div className="flex items-center justify-between">
                                    <label className="text-sm font-medium text-gray-500">F. Registro</label>
                                    <p className="text-sm text-gray-900">
                                        {formatDate(currentEmployee.date_joined)}
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center justify-end gap-3 pt-4 mt-4 border-t">
                            <button
                                type="button"
                                onClick={() => setShowDetailsModal(false)}
                                className="px-4 py-2 rounded-md border bg-gray-50 text-gray-700 font-medium hover:bg-gray-100"
                            >
                                Cerrar
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}