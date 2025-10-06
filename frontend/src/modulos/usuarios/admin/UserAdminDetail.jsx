// src/pages/admin/UserAdminDetail.jsx
import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { adminGetUser, adminGetActivityLog } from "../../../services/adminUsers";

export default function UserAdminDetail() {
  const { id } = useParams();
  const [user, setUser] = useState(null);
  const [log, setLog] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const res = await adminGetUser(id);
        setUser(res.data);
        // intentar traer actividad
        const logRes = await adminGetActivityLog(id);
        setLog(logRes.data.recent_activity ?? logRes.data);
      } catch (err) {
        alert("Error al cargar detalle");
      } finally { setLoading(false); }
    })();
  }, [id]);

  if (loading) return <div className="p-6">Cargando...</div>;
  if (!user) return <div className="p-6">Usuario no encontrado</div>;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">Detalle: {user.username}</h2>
        <div>
          <Link to={`/admin/users/${id}/edit`} className="mr-2 text-indigo-600">Editar</Link>
          <Link to="/admin/users" className="text-gray-600">Volver</Link>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white p-4 rounded shadow">
          <p><strong>Nombre:</strong> {user.full_name}</p>
          <p><strong>Email:</strong> {user.email}</p>
          <p><strong>Activo:</strong> {user.is_active ? "Sí" : "No"}</p>
          <p><strong>Rol actual:</strong> {user.rol_actual?.nombre ?? "—"}</p>
          <p><strong>Último login:</strong> {user.last_login ?? "—"}</p>
        </div>

        <div className="bg-white p-4 rounded shadow">
          <h3 className="font-semibold mb-2">Actividad reciente</h3>
          {!log.length ? <div>No hay actividad</div> : (
            <ul className="space-y-2">
              {log.map(entry => (
                <li key={entry.id} className="text-sm border-b pb-1">
                  <div><strong>{entry.action}</strong></div>
                  <div className="text-xs">{entry.date} — {entry.ip}</div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
