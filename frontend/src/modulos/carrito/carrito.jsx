import { useState, useEffect } from "react";
import API from "../../services/api"; // tu servicio Axios

export default function Carrito() {
  const [productos, setProductos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Traer los productos del carrito desde Django
  useEffect(() => {
    const fetchCarrito = async () => {
      try {
        const token = localStorage.getItem("token");
        const res = await API.get("carrito/", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setProductos(res.data);
        setLoading(false);
      } catch (err) {
        setError("No se pudo cargar el carrito");
        setLoading(false);
      }
    };
    fetchCarrito();
  }, []);

  // Calcular total
  const total = productos.reduce((acc, prod) => acc + prod.precio * prod.cantidad, 0);

  return (
    <section id="carrito" className="py-16 bg-slate-50 min-h-screen">
      <div className="container mx-auto px-6 max-w-4xl">
        <h2 className="text-3xl font-bold mb-8 text-center text-slate-800">
          Tu Carrito
        </h2>

        {loading ? (
          <p className="text-center text-slate-500">Cargando...</p>
        ) : error ? (
          <p className="text-center text-red-500">{error}</p>
        ) : productos.length === 0 ? (
          <p className="text-center text-slate-500">Tu carrito está vacío</p>
        ) : (
          <div className="bg-white p-6 rounded-3xl shadow-xl border border-slate-100">
            <ul className="divide-y divide-slate-200">
              {productos.map((prod) => (
                <li key={prod.id} className="flex justify-between py-4 items-center">
                  <div className="flex items-center gap-4">
                    <img
                      src={prod.imagen || "/placeholder.png"}
                      alt={prod.nombre}
                      className="w-16 h-16 object-cover rounded-lg"
                    />
                    <div>
                      <h3 className="text-lg font-semibold text-slate-800">{prod.nombre}</h3>
                      <p className="text-slate-500 text-sm">{prod.descripcion}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-slate-800 font-semibold">{prod.cantidad}x</span>
                    <span className="text-slate-700 font-medium">${prod.precio.toFixed(2)}</span>
                  </div>
                </li>
              ))}
            </ul>

            <div className="mt-6 flex justify-between items-center font-semibold text-lg text-slate-800">
              <span>Total:</span>
              <span>${total.toFixed(2)}</span>
            </div>

            <button
              className="w-full mt-6 bg-gradient-to-r from-blue-500 to-purple-500 text-white py-3 rounded-full font-semibold hover:shadow-lg hover:shadow-purple-300/40 transform hover:scale-105 transition-all duration-300"
              onClick={() => alert("Checkout listo para implementar")}
            >
              Ir a pagar
            </button>
          </div>
        )}
      </div>
      <div></div>
    </section>
  );
}
