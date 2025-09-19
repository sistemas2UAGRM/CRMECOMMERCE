import { Trash2, Edit } from "lucide-react";

export default function PerfilCard({ perfil }) {
  return (
    <div className="bg-white p-6 rounded-2xl shadow-lg border border-slate-100 flex flex-col items-center text-center">
      <img
        src={perfil.avatar || "/placeholder.png"}
        alt={perfil.nombre}
        className="w-24 h-24 rounded-full mb-4 object-cover"
      />
      <h3 className="text-lg font-semibold text-slate-800">{perfil.nombre}</h3>
      <p className="text-slate-500">{perfil.email}</p>
      <p className="text-sm text-slate-400">{perfil.rol}</p>

      <div className="flex gap-4 mt-4">
        <button className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition">
          <Edit className="w-4 h-4 inline mr-1" /> Editar
        </button>
        <button className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition">
          <Trash2 className="w-4 h-4 inline mr-1" /> Eliminar
        </button>
      </div>
    </div>
  );
}
