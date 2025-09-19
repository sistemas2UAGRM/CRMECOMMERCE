import { useState } from "react";
import { Mail, Lock } from "lucide-react"; // íconos de ejemplo
import API from "../services/api";

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
    <section id="login" className="py-20 bg-slate-50 min-h-screen flex items-center justify-center">
      <div className="container mx-auto px-6 max-w-md">
        <div className="bg-white p-10 rounded-3xl shadow-xl border border-slate-100">
          <h3 className="text-3xl font-bold mb-8 text-center bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent">
            Accede a tu cuenta
          </h3>
          <form className="space-y-6" onSubmit={handleLogin}>
            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-slate-700 font-medium mb-2">
                Email
              </label>
              <div className="relative group">
                <Mail className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="correo@ejemplo.com"
                  className="w-full pl-10 pr-3 py-2.5 border border-slate-200 rounded-xl outline-none transition-all duration-300 focus:ring-2 focus:ring-blue-400 focus:border-blue-400"
                  required
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-slate-700 font-medium mb-2">
                Contraseña
              </label>
              <div className="relative group">
                <Lock className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="********"
                  className="w-full pl-10 pr-3 py-2.5 border border-slate-200 rounded-xl outline-none transition-all duration-300 focus:ring-2 focus:ring-blue-400 focus:border-blue-400"
                  required
                />
              </div>
            </div>

            {/* Error */}
            {error && <p className="text-red-500 text-sm">{error}</p>}

            {/* Submit */}
            <button
              type="submit"
              className="w-full bg-gradient-to-r from-blue-500 to-purple-500 text-white py-3 rounded-full font-semibold hover:shadow-lg hover:shadow-purple-300/40 transform hover:scale-105 transition-all duration-300"
            >
              Ingresar
            </button>
          </form>

          <p className="text-center text-slate-500 text-sm mt-6">
            ¿No tienes cuenta?{" "}
            <a href="#plans" className="font-semibold text-blue-500 hover:underline">
              Regístrate ahora
            </a>
          </p>
        </div>
      </div>
    </section>
  );
}
