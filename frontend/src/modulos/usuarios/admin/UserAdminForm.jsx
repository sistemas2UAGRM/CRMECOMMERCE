// src/pages/admin/UserAdminForm.jsx
import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { adminCreateUser, adminGetUser, adminUpdateUser } from "../../../services/adminUsers";

/**
 * Formulario simple para crear / editar usuario por admin.
 * Campos basicos basados en tus serializers: username, email, first_name, last_name, fecha_de_nacimiento, sexo, celular, rol
 * Para rol usamos campo 'rol' del AdminUserRegistrationSerializer.
 *
 * NOTA: backend puede ignorar password si no se pasa. En creación admin puede enviar rol.
 */
export default function UserAdminForm() {
  const { id } = useParams();
  const nav = useNavigate();
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
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

  useEffect(() => {
    if (id) {
      (async () => {
        setLoading(true);
        try {
          const res = await adminGetUser(id);
          const d = res.data;
          // mapear campos que esperas editar (no todos están en UserDetailSerializer; pero admin GET usa UserDetailSerializer)
          setForm({
            username: d.username ?? "",
            email: d.email ?? "",
            first_name: d.first_name ?? "",
            last_name: d.last_name ?? "",
            fecha_de_nacimiento: d.fecha_de_nacimiento ?? "",
            sexo: d.sexo ?? "",
            celular: d.celular ?? "",
            rol: d.rol_actual?.nombre ?? "cliente",
            password: "" // no traer password
          });
        } catch (err) {
          alert("No se pudo cargar usuario");
        } finally { setLoading(false); }
      })();
    }
  }, [id]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});
    setLoading(true);
    try {
      if (id) {
        // actualizar: Admin puede usar PATCH para cambiar rol/otros — aqui usamos PUT para simplicidad
        const payload = {
          username: form.username,
          email: form.email,
          first_name: form.first_name,
          last_name: form.last_name,
          fecha_de_nacimiento: form.fecha_de_nacimiento,
          sexo: form.sexo,
          celular: form.celular,
          // no necesariamente backend espera 'rol' en PUT; AdminUserRegistrationSerializer espera 'rol' en create.
        };
        // Si se cambió rol, podríamos usar patch
        await adminUpdateUser(id, payload);
        alert("Usuario actualizado");
      } else {
        // crear usuario por admin: usar campo 'rol' y opcional password
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
      nav("/admin/users");
    } catch (err) {
      const resp = err.response?.data;
      setErrors(resp || { non_field_errors: ["Error desconocido"] });
    } finally { setLoading(false); }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded shadow">
      <h2 className="text-xl font-bold mb-4">{id ? "Editar usuario" : "Crear usuario (admin)"}</h2>

      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <label className="block text-sm">Usuario</label>
          <input name="username" value={form.username} onChange={handleChange} className="w-full p-2 border rounded" />
          {errors.username && <div className="text-red-600">{errors.username}</div>}
        </div>

        <div>
          <label className="block text-sm">Email</label>
          <input name="email" value={form.email} onChange={handleChange} className="w-full p-2 border rounded" />
          {errors.email && <div className="text-red-600">{errors.email}</div>}
        </div>

        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="block text-sm">Nombre</label>
            <input name="first_name" value={form.first_name} onChange={handleChange} className="w-full p-2 border rounded" />
          </div>
          <div>
            <label className="block text-sm">Apellido</label>
            <input name="last_name" value={form.last_name} onChange={handleChange} className="w-full p-2 border rounded" />
          </div>
        </div>

        <div className="grid grid-cols-3 gap-2">
          <div>
            <label className="block text-sm">Fecha Nac.</label>
            <input type="date" name="fecha_de_nacimiento" value={form.fecha_de_nacimiento} onChange={handleChange} className="w-full p-2 border rounded" />
          </div>
          <div>
            <label className="block text-sm">Sexo</label>
            <select name="sexo" value={form.sexo} onChange={handleChange} className="w-full p-2 border rounded">
              <option value="">--</option>
              <option value="M">M</option>
              <option value="F">F</option>
              <option value="O">Otro</option>
            </select>
          </div>
          <div>
            <label className="block text-sm">Celular</label>
            <input name="celular" value={form.celular} onChange={handleChange} className="w-full p-2 border rounded" />
          </div>
        </div>

        {!id && (
          <>
            <div>
              <label className="block text-sm">Rol</label>
              <select name="rol" value={form.rol} onChange={handleChange} className="w-full p-2 border rounded">
                <option value="cliente">cliente</option>
                <option value="empleadonivel2">empleadonivel2</option>
                <option value="empleadonivel1">empleadonivel1</option>
                <option value="administrador">administrador</option>
              </select>
            </div>

            <div>
              <label className="block text-sm">Contraseña (opcional, si vacío genera temporal)</label>
              <input name="password" value={form.password} onChange={handleChange} className="w-full p-2 border rounded" type="password" />
            </div>
          </>
        )}

        {Object.keys(errors).length > 0 && (
          <div className="text-red-600">
            {Array.isArray(errors) ? errors.join(", ") : JSON.stringify(errors)}
          </div>
        )}

        <div className="flex gap-2">
          <button disabled={loading} type="submit" className="px-4 py-2 bg-blue-600 text-white rounded">
            {loading ? "Guardando..." : "Guardar"}
          </button>
          <button type="button" onClick={() => window.history.back()} className="px-4 py-2 border rounded">Cancelar</button>
        </div>
      </form>
    </div>
  );
}
