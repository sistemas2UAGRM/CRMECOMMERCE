// frontend/src/modulos/usuarios/admin/UserForm.jsx
import React, { useState, useEffect } from 'react';

export default function UserForm({ usuarioInicial, onSubmit, onCancelar, cargando }) {
  const [form, setForm] = useState({
    username: '', email: '', first_name: '', last_name: '',
    // --- CAMPOS NUEVOS ---
    celular: '', 
    fecha_de_nacimiento: '',
    sexo: '',
    // --- FIN CAMPOS NUEVOS ---
    rol: 'cliente', password: '',
  });

  const esModoCrear = !usuarioInicial;

  useEffect(() => {
    if (usuarioInicial) {
      setForm({
        username: usuarioInicial.username || '',
        email: usuarioInicial.email || '',
        first_name: usuarioInicial.first_name || '',
        last_name: usuarioInicial.last_name || '',
        // --- CAMPOS NUEVOS ---
        celular: usuarioInicial.celular || '',
        fecha_de_nacimiento: usuarioInicial.fecha_de_nacimiento || '',
        sexo: usuarioInicial.sexo || '',
        // --- FIN CAMPOS NUEVOS ---
        rol: usuarioInicial.rol_actual?.nombre || 'cliente',
        password: '',
      });
    } else {
        // Resetear para modo crear
        setForm({
            username: '', email: '', first_name: '', last_name: '',
            celular: '', fecha_de_nacimiento: '', sexo: '', // Resetear
            rol: 'cliente', password: '',
        });
    }
  }, [usuarioInicial]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const payload = { ...form };
    
    if (esModoCrear) {
        if (!payload.password) {
            delete payload.password; // No enviar contraseña vacía
        }
    } else {
        // En modo EDITAR, no enviamos rol ni password
        delete payload.rol;
        delete payload.password;
    }

    // Limpiar campos nulos que Django no acepta
    if (!payload.fecha_de_nacimiento) payload.fecha_de_nacimiento = null;
    if (!payload.celular) payload.celular = null;
    if (!payload.sexo) payload.sexo = null;

    onSubmit(payload);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm">Username</label>
          <input name="username" value={form.username} onChange={handleChange} className="w-full border rounded p-2" required />
        </div>
        <div>
          <label className="block text-sm">Email</label>
          <input name="email" type="email" value={form.email} onChange={handleChange} className="w-full border rounded p-2" required />
        </div>
        <div>
          <label className="block text-sm">Nombre</label>
          <input name="first_name" value={form.first_name} onChange={handleChange} className="w-full border rounded p-2" />
        </div>
        <div>
          <label className="block text-sm">Apellido</label>
          <input name="last_name" value={form.last_name} onChange={handleChange} className="w-full border rounded p-2" />
        </div>
        
        {/* --- NUEVOS CAMPOS (Solo para editar) --- */}
        {!esModoCrear && (
          <>
            <div>
              <label className="block text-sm">Celular</label>
              <input name="celular" value={form.celular || ''} onChange={handleChange} className="w-full border rounded p-2" placeholder="Ej: +5917..." />
            </div>
            <div>
              <label className="block text-sm">Fecha de Nacimiento</label>
              <input name="fecha_de_nacimiento" type="date" value={form.fecha_de_nacimiento || ''} onChange={handleChange} className="w-full border rounded p-2" />
            </div>
            <div>
              <label className="block text-sm">Sexo</label>
              <select name="sexo" value={form.sexo || ''} onChange={handleChange} className="w-full border rounded p-2">
                <option value="">No especificar</option>
                <option value="M">Masculino</option>
                <option value="F">Femenino</option>
                <option value="O">Otro</option>
              </select>
            </div>
          </>
        )}
        
        {/* --- CAMPOS DE CREACIÓN --- */}
        {esModoCrear && (
          <>
            <div>
              <label className="block text-sm">Rol</label>
              <select name="rol" value={form.rol} onChange={handleChange} className="w-full border rounded p-2">
                <option value="cliente">Cliente</option>
                <option value="empleadonivel2">Vendedor</option>
                <option value="empleadonivel1">Supervisor</option>
                <option value="administrador">Administrador</option>
              </select>
            </div>
            <div>
              <label className="block text-sm">Contraseña</label>
              <input name="password" type="password" value={form.password} onChange={handleChange} className="w-full border rounded p-2" placeholder="Dejar vacío para autogenerar" />
            </div>
          </>
        )}
      </div>

      <div className="flex justify-end gap-3 pt-4">
        <button type="button" onClick={onCancelar} className="px-4 py-2 border rounded">Cancelar</button>
        <button type="submit" disabled={cargando} className="px-4 py-2 bg-indigo-600 text-white rounded disabled:bg-indigo-300">
          {cargando ? 'Guardando...' : 'Guardar'}
        </button>
      </div>
    </form>
  );
}