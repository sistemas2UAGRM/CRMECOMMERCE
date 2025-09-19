import { Link } from "react-router-dom";

function Register() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
      <section className="w-full max-w-md bg-white rounded-2xl shadow-lg p-8">
        
        {/* Header */}
        <header className="text-center mb-8">
          <h1 className="text-3xl font-bold text-[#2e7e8b]">Crear cuenta</h1>
          <p className="text-slate-600 mt-2">Únete a nuestra plataforma en segundos</p>
        </header>

        {/* Formulario */}
        <form className="space-y-5">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-slate-700">
              Nombre completo
            </label>
            <input
              type="text"
              id="name"
              placeholder="Ej. Ana Pérez"
              className="mt-1 w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2e7e8b] border-slate-300"
              required
            />
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-slate-700">
              Correo electrónico
            </label>
            <input
              type="email"
              id="email"
              placeholder="ejemplo@correo.com"
              className="mt-1 w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2e7e8b] border-slate-300"
              required
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-slate-700">
              Contraseña
            </label>
            <input
              type="password"
              id="password"
              placeholder="********"
              className="mt-1 w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2e7e8b] border-slate-300"
              required
            />
          </div>

          <div>
            <label htmlFor="confirm-password" className="block text-sm font-medium text-slate-700">
              Confirmar contraseña
            </label>
            <input
              type="password"
              id="confirm-password"
              placeholder="********"
              className="mt-1 w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#2e7e8b] border-slate-300"
              required
            />
          </div>

          <button
            type="submit"
            className="w-full py-3 rounded-lg font-semibold text-white bg-[#2e7e8b] hover:bg-[#256773] transition-colors duration-300"
          >
            Registrarse
          </button>
        </form>

        {/* Footer */}
        <footer className="text-center mt-6 text-sm text-slate-600">
          ¿Ya tienes cuenta?{" "}
          <Link to="/login" className="font-semibold text-[#f0a831] hover:underline">
            Inicia sesión
          </Link>
        </footer>
      </section>
    </main>
  );
}

export default Register;
