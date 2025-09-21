export default function CarritosPage() {
  return (
    <section className="py-20 bg-slate-50 min-h-screen flex items-center justify-center">
      <div className="container mx-auto px-6 max-w-md">
        <div className="bg-white p-10 rounded-3xl shadow-xl border border-slate-100">
          <h3 className="text-3xl font-bold mb-8 text-center bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Gestión de Carritos
          </h3>
          <form className="space-y-6">
            <div>
              <label className="block text-slate-700 font-medium mb-2">ID del usuario</label>
              <input type="number" placeholder="Ejemplo: 1" className="w-full px-4 py-2.5 border border-slate-200 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
            </div>
            <div>
              <label className="block text-slate-700 font-medium mb-2">Estado del carrito</label>
              <input type="text" placeholder="Ejemplo: ABIERTO" className="w-full px-4 py-2.5 border border-slate-200 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
            </div>
            <button type="submit" className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-full font-semibold hover:shadow-lg hover:shadow-purple-500/40 transform hover:scale-105 transition-all duration-300">
              Guardar Carrito
            </button>
          </form>
        </div>
      </div>
    </section>
  );
}
