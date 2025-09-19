import { useState } from "react";
import { Mail, Lock } from "lucide-react";
import API from "../services/api";
import { Link } from "react-router-dom";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await API.post("token/", { username: email, password });
      localStorage.setItem("token", res.data.access);
      alert("Login exitoso 🚀");
      setError("");
    } catch (err) {
      setError("Credenciales inválidas");
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
      <section className="w-full max-w-md bg-white rounded-2xl shadow-lg p-8">
        
        {/* Header */}
        <header className="text-center mb-8">
          <h1 className="text-3xl font-bold text-[#2e7e8b]">Accede a tu cuenta</h1>
          <p className="text-slate-600 mt-2">Bienvenido de nuevo</p>
        </header>

        {/* Formulario */}
        <form className="space-y-6" onSubmit={handleLogin}>
          {/* Email */}
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-slate-700 mb-1"
            >
              Correo electrónico
            </label>
            <div className="relative">
              <Mail className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="correo@ejemplo.com"
                className="w-full pl-10 pr-3 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-[#2e7e8b] focus:border-[#2e7e8b] transition-all"
                required
              />
            </div>
          </div>

          {/* Password */}
          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-slate-700 mb-1"
            >
              Contraseña
            </label>
            <div className="relative">
              <Lock className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="********"
                className="w-full pl-10 pr-3 py-2 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-[#2e7e8b] focus:border-[#2e7e8b] transition-all"
                required
              />
            </div>
          </div>

          {/* Error */}
          {error && <p className="text-red-500 text-sm">{error}</p>}

          {/* Submit */}
          <button
            type="submit"
            className="w-full py-3 rounded-lg font-semibold text-white bg-[#2e7e8b] hover:bg-[#256773] transition-colors duration-300"
          >
            Ingresar
          </button>
        </form>

        {/* Footer */}
        <footer className="text-center mt-6 text-sm text-slate-600">
          ¿No tienes cuenta?{" "}
          <Link to="/registro" className="font-semibold text-[#f0a831] hover:underline">
            Regístrate ahora
          </Link>
        </footer>
      </section>
    </main>
  );
}
