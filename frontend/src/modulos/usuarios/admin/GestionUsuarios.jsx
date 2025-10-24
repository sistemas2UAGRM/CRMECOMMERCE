// src/modulos/usuarios/admin/GestionUsuarios.jsx
import React, { useEffect, useState } from "react";
import { useUsers } from "../hooks/useUsers";
import usersService from "../../../services/usersService";
import toast from "react-hot-toast";

import UserTable from "./UserTable";
import UserForm from "./UserForm";
import Modal from "../../productos/Modal"

import {
  Users, Search, Plus, RefreshCw, Eye, Edit2, Trash2, UserCheck,
  UserX, X, Save, ChevronLeft, ChevronRight, Mail, Phone,
  Calendar, Shield, Activity, AlertCircle, Filter, FilterX,
  SlidersHorizontal, ChevronDown, ChevronUp,
} from "lucide-react";


export default function GestionUsuarios() {
  const {
    usuarios, cargando, error, meta,
    obtenerUsuarios, crearUsuario, actualizarUsuario, eliminarUsuario
  } = useUsers();

  const [modalAbierto, setModalAbierto] = useState(false);
  const [usuarioSeleccionado, setUsuarioSeleccionado] = useState(null);
  const [modo, setModo] = useState('crear'); 
  
  const [filtros, setFiltros] = useState({ page: 1, search: "" });

  useEffect(() => {
    obtenerUsuarios(filtros);
  }, [filtros, obtenerUsuarios]);

  const abrirModalCrear = () => {
    setUsuarioSeleccionado(null);
    setModo('crear');
    setModalAbierto(true);
  };

  const abrirModalEditar = async (usuario) => {
    try {
        const datosCompletos = await usersService.detalle(usuario.id);
        setUsuarioSeleccionado(datosCompletos);
        setModo('editar');
        setModalAbierto(true);
    } catch (err) {
        toast.error("No se pudieron cargar los datos del usuario.");
    }
  };

  const handleCerrarModal = () => {
    setModalAbierto(false);
    setUsuarioSeleccionado(null);
  };
  
  const handleSubmit = async (datosFormulario) => {
    try {
      if (modo === 'crear') {
        await crearUsuario(datosFormulario);
      } else {
        await actualizarUsuario(usuarioSeleccionado.id, datosFormulario);
      }
      handleCerrarModal();
    } catch (err) {
      console.error("Fallo el submit:", err);
    }
  };

  const handleEliminar = (usuario) => {
    if (window.confirm(`¿Estás seguro de eliminar a ${usuario.username}?`)) {
        eliminarUsuario(usuario.id);
    }
  };

  const handleToggleActive = (usuario) => {
    const accion = usuario.is_active ? "desactivar" : "activar";
    if (window.confirm(`¿Estás seguro de ${accion} a ${usuario.username}?`)) {
        actualizarUsuario(usuario.id, { is_active: !usuario.is_active });
    }
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold flex items-center gap-2"><Users /> Gestión de Usuarios</h1>
        <div>
          <button onClick={() => obtenerUsuarios(filtros)} className="mr-2 p-2 border rounded"><RefreshCw className={cargando ? 'animate-spin' : ''} /></button>
          <button onClick={abrirModalCrear} className="px-4 py-2 bg-green-600 text-white rounded flex items-center gap-2"><Plus /> Nuevo Usuario</button>
        </div>
      </div>

      <div className="mb-4">
        <input 
          type="text"
          placeholder="Buscar por nombre, email..."
          className="w-full p-2 border rounded"
          onChange={(e) => setFiltros(f => ({ ...f, search: e.target.value, page: 1 }))}
        />
      </div>

      {error && <p className="text-red-500">Error al cargar datos.</p>}

      <UserTable 
        usuarios={usuarios}
        onEditar={abrirModalEditar}
        onEliminar={handleEliminar}
        onToggleActive={handleToggleActive}
        cargando={cargando}
      />

      {/* Paginación */}
      {meta && (
        <div className="mt-6 flex justify-between items-center">
          <div>Total: {meta.count}</div>
          <div className="space-x-2">
            <button disabled={!meta.previous} onClick={() => setFiltros(f => ({...f, page: f.page - 1}))} className="px-3 py-1 border rounded disabled:opacity-50">Anterior</button>
            <span>Página {filtros.page}</span>
            <button disabled={!meta.next} onClick={() => setFiltros(f => ({...f, page: f.page + 1}))} className="px-3 py-1 border rounded disabled:opacity-50">Siguiente</button>
          </div>
        </div>
      )}

      {/* Modal para Crear/Editar */}
      <Modal 
        abierto={modalAbierto}
        titulo={modo === 'crear' ? 'Crear Nuevo Usuario' : 'Editar Usuario'}
        onCerrar={handleCerrarModal}
      >
        <UserForm 
          usuarioInicial={usuarioSeleccionado}
          onSubmit={handleSubmit}
          onCancelar={handleCerrarModal}
          cargando={cargando}
        />
      </Modal>
    </div>
  );
}