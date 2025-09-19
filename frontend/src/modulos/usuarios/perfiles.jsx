import { useState, useEffect } from "react";
import API from "../../services/api";
import PerfilCard from "./perfilcard";

export default function Perfiles() {
  const [perfiles, setPerfiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchPerfiles = async () => {
      try {
        const token = localStorage.getItem("token");
        const res = await API.get("usuarios/", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setPerfiles(res.data);
        setLoading(false);
      } catch (err) {
        setError("No se pudo cargar los perfiles");
        setLoading(false);
      }
    };
    fetchPerfiles();
  }, []);

  return (
    <section className="py-16 bg-slate-50 min-h-screen">
      <div className="container mx-auto px-6 max-w-5xl">
        <h2 className="text-3xl font-bold mb-8 text-center text-slate-800">
          Gestión de Perfiles
        </h2>

        {loading ? (
          <p className="text-center text-slate-500">Cargando perfiles...</p>
        ) : error ? (
          <p className="text-center text-red-500">{error}</p>
        ) : perfiles.length === 0 ? (
          <p className="text-center text-slate-500">No hay perfiles registrados</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {perfiles.map((perfil) => (
              <PerfilCard key={perfil.id} perfil={perfil} />
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
