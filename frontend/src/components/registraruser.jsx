import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../services/api";

function Register() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    password_confirm: "",
    first_name: "",
    last_name: "",
    fecha_de_nacimiento: "",
    sexo: "",
    celular: "",
    acepta_terminos: false,
    acepta_marketing: false,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Manejar cambios en inputs
  const handleChange = (e) => {
    const { id, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [id]: type === "checkbox" ? checked : value,
    });
  };

  // Manejar envío
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");

    if (formData.password !== formData.password_confirm) {
      setError("Las contraseñas no coinciden");
      setLoading(false);
      return;
    }

    try {
      const response = await api.post("/users/register/", formData);
      
      if (response.status === 201 || response.status === 200) {
        setSuccess(response.data?.message || "Usuario registrado exitosamente.");
        setTimeout(() => Link("/login"), 2000);
      } else {
        setError("Error al registrar usuario.");
      }
    } catch (err) {
      if (err.response?.data) {
          const data = err.response.data;
          if (typeof data === "object") {
            const mensajes = Object.values(data)
              .flat()
              .map((m) => (typeof m === "string" ? m : JSON.stringify(m)))
              .join(" ");
            setError(mensajes);
          } else if (typeof data === "string") {
            setError(data);
          } else {
            setError("Error al registrar usuario.");
          }
        } else {
          setError("Error al conectar con el servidor.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-slate-100 to-slate-200 px-4 py-8">
      <section className="w-full max-w-lg bg-white rounded-3xl shadow-2xl p-8 transform transition-all duration-500 hover:shadow-3xl">
        {/* Header */}
        <header className="text-center mb-10">
          <div className="mb-6">
            <div className="w-16 h-16 bg-gradient-to-r from-[#2e7e8b] to-[#1e5a64] rounded-full mx-auto flex items-center justify-center shadow-lg transform transition-transform duration-300 hover:scale-105">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
          </div>
          <h1 className="text-4xl font-bold text-[#2e7e8b] mb-3 tracking-tight">Crear cuenta</h1>
          <p className="text-slate-600 text-lg font-medium">Únete a nuestra plataforma profesional</p>
        </header>

        {/* Formulario */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Nombre y Apellido */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input
              id="first_name"
              type="text"
              placeholder="Nombre"
              value={formData.first_name}
              onChange={handleChange}
              required
              className="w-full px-4 py-4 border-2 border-slate-200 rounded-xl text-slate-800 placeholder-slate-400 focus:border-[#2e7e8b] focus:ring-4 focus:ring-[#2e7e8b]/10 focus:outline-none bg-slate-50/50 focus:bg-white"
            />
            <input
              id="last_name"
              type="text"
              placeholder="Apellido"
              value={formData.last_name}
              onChange={handleChange}
              required
              className="w-full px-4 py-4 border-2 border-slate-200 rounded-xl text-slate-800 placeholder-slate-400 focus:border-[#2e7e8b] focus:ring-4 focus:ring-[#2e7e8b]/10 focus:outline-none bg-slate-50/50 focus:bg-white"
            />
          </div>

          {/* Usuario */}
          <input
            id="username"
            type="text"
            placeholder="Nombre de usuario"
            value={formData.username}
            onChange={handleChange}
            required
            className="w-full px-4 py-4 border-2 border-slate-200 rounded-xl text-slate-800 placeholder-slate-400 focus:border-[#2e7e8b] focus:ring-4 focus:ring-[#2e7e8b]/10 focus:outline-none bg-slate-50/50 focus:bg-white"
          />

          {/* Email */}
          <input
            id="email"
            type="email"
            placeholder="Correo electrónico"
            value={formData.email}
            onChange={handleChange}
            required
            className="w-full px-4 py-4 border-2 border-slate-200 rounded-xl text-slate-800 placeholder-slate-400 focus:border-[#2e7e8b] focus:ring-4 focus:ring-[#2e7e8b]/10 focus:outline-none bg-slate-50/50 focus:bg-white"
          />

          {/* Celular y Fecha */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input
              id="celular"
              type="text"
              placeholder="Número de celular"
              value={formData.celular}
              onChange={handleChange}
              required
              className="w-full px-4 py-4 border-2 border-slate-200 rounded-xl text-slate-800 placeholder-slate-400 focus:border-[#2e7e8b] focus:ring-4 focus:ring-[#2e7e8b]/10 focus:outline-none bg-slate-50/50 focus:bg-white"
            />
            <input
              id="fecha_de_nacimiento"
              type="date"
              value={formData.fecha_de_nacimiento}
              onChange={handleChange}
              required
              className="w-full px-4 py-4 border-2 border-slate-200 rounded-xl text-slate-800 focus:border-[#2e7e8b] focus:ring-4 focus:ring-[#2e7e8b]/10 focus:outline-none bg-slate-50/50 focus:bg-white"
            />
          </div>

          {/* Sexo */}
          <select
            id="sexo"
            value={formData.sexo}
            onChange={handleChange}
            required
            className="w-full px-4 py-4 border-2 border-slate-200 rounded-xl text-slate-800 focus:border-[#2e7e8b] focus:ring-4 focus:ring-[#2e7e8b]/10 focus:outline-none bg-slate-50/50 appearance-none cursor-pointer"
          >
            <option value="" disabled>Seleccionar sexo</option>
            <option value="M">Masculino</option>
            <option value="F">Femenino</option>
            <option value="O">Otro</option>
          </select>

          {/* Contraseñas */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input
              id="password"
              type="password"
              placeholder="Contraseña"
              value={formData.password}
              onChange={handleChange}
              required
              className="w-full px-4 py-4 border-2 border-slate-200 rounded-xl text-slate-800 placeholder-slate-400 focus:border-[#2e7e8b] focus:ring-4 focus:ring-[#2e7e8b]/10 focus:outline-none bg-slate-50/50"
            />
            <input
              id="password_confirm"
              type="password"
              placeholder="Confirmar contraseña"
              value={formData.password_confirm}
              onChange={handleChange}
              required
              className="w-full px-4 py-4 border-2 border-slate-200 rounded-xl text-slate-800 placeholder-slate-400 focus:border-[#2e7e8b] focus:ring-4 focus:ring-[#2e7e8b]/10 focus:outline-none bg-slate-50/50"
            />
          </div>

          {/* Checkboxes */}
          <div className="space-y-4 pt-4">
            <label className="flex items-start space-x-3 cursor-pointer">
              <input
                id="acepta_terminos"
                type="checkbox"
                checked={formData.acepta_terminos}
                onChange={handleChange}
                required
                className="mt-1 w-5 h-5 text-[#2e7e8b] border-2 border-slate-300 rounded focus:ring-[#2e7e8b] focus:ring-2"
              />
              <span className="text-slate-700 text-sm">
                Acepto los <a href="/terms" className="text-[#2e7e8b] font-semibold underline">términos y condiciones</a>
              </span>
            </label>

            <label className="flex items-start space-x-3 cursor-pointer">
              <input
                id="acepta_marketing"
                type="checkbox"
                checked={formData.acepta_marketing}
                onChange={handleChange}
                className="mt-1 w-5 h-5 text-[#f0a831] border-2 border-slate-300 rounded focus:ring-[#f0a831] focus:ring-2"
              />
              <span className="text-slate-700 text-sm">
                Deseo recibir promociones y ofertas especiales por correo electrónico
              </span>
            </label>
          </div>

          {/* Botón de registro */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-[#2e7e8b] to-[#1e5a64] text-white font-bold py-4 px-8 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 text-lg"
          >
            {loading ? "Registrando..." : "Crear cuenta"}
          </button>

          {/* Mensajes de estado */}
          {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
          {success && <p className="text-green-600 text-sm mt-2">{success}</p>}
        </form>

        {/* Footer */}
        <footer className="text-center mt-8 pt-6 border-t border-slate-100">
          <p className="text-slate-600 text-sm">
            ¿Ya tienes una cuenta?{" "}
            <Link to="/login" className="font-bold text-[#f0a831] hover:text-[#e09520] transition-colors duration-200 hover:underline">
              Inicia sesión aquí
            </Link>
          </p>
        </footer>
      </section>
    </main>
  );
}

export default Register;