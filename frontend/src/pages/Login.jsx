import { Mail, Lock } from "lucide-react";

export default function LoginPage() {
  return (
    <section className="py-20 bg-slate-50 min-h-screen flex items-center justify-center">
      <div className="container mx-auto px-6 max-w-md">
        <div className="bg-white p-10 rounded-3xl shadow-xl border border-slate-100">
          <h3 className="text-3xl font-bold mb-8 text-center bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Accede a tu cuenta
          </h3>
          <form className="space-y-6">
            <div>
              <label className="block text-slate-700 font-medium mb-2">Email</label>
              <div className="relative group">
                <Mail className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input type="email" placeholder="correo@ejemplo.com" className="w-full pl-10 pr-3 py-2.5 border border-slate-200 rounded-xl outline-none transition-all duration-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
              </div>
            </div>
            <div>
              <label className="block text-slate-700 font-medium mb-2">Contraseña</label>
              <div className="relative group">
                <Lock className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input type="password" placeholder="********" className="w-full pl-10 pr-3 py-2.5 border border-slate-200 rounded-xl outline-none transition-all duration-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
              </div>
            </div>
            <button type="submit" className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-full font-semibold hover:shadow-lg hover:shadow-purple-500/40 transform hover:scale-105 transition-all duration-300">
              Ingresar
            </button>
          </form>
          <p className="text-center text-slate-500 text-sm mt-6">
            ¿No tienes cuenta? <a href="/register" className="font-semibold text-blue-600 hover:underline">Regístrate ahora</a>
          </p>
        </div>
      </div>
    </section>
  );
}
