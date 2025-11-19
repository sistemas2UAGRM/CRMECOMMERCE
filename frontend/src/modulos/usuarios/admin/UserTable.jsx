// frontend/src/modulos/usuarios/admin/UserTable.jsx
import React from 'react';
import { Edit, Trash2, UserCheck, UserX, MoreHorizontal } from 'lucide-react';

export default function UserTable({
  usuarios = [],
  onEditar,
  onEliminar,
  onToggleActive,
  cargando = false,
}) {
  if (cargando) {
    // Skeleton simple
    return (
      <div className="space-y-4">
        {[1,2,3].map(i => (
          <div key={i} className="bg-white p-4 rounded-lg animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/3 mb-2" />
            <div className="h-3 bg-gray-200 rounded w-1/2" />
          </div>
        ))}
      </div>
    );
  }

  if (!usuarios || usuarios.length === 0) {
    return (
      <div className="bg-white p-6 rounded shadow text-center">
        <p className="text-gray-600">No hay usuarios para mostrar.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* MOBILE: cards */}
      <div className="grid grid-cols-1 gap-4 md:hidden">
        {usuarios.map(user => {
          const role = user.role ?? user.rol ?? 'Cliente';
          return (
            <article key={user.id} className="bg-white p-4 rounded-lg shadow hover:shadow-lg transition-shadow" role="listitem">
              <div className="flex items-start justify-between">
                <div>
                  <div className="font-semibold text-gray-900">{user.username}</div>
                  <div className="text-sm text-gray-500">{user.full_name ?? `${user.first_name} ${user.last_name}`}</div>
                  <div className="text-sm text-gray-500 truncate">{user.email}</div>
                </div>
                <div className="text-right">
                  <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full ${user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                    {user.is_active ? 'Activo' : 'Inactivo'}
                  </span>
                </div>
              </div>

              <div className="mt-3 flex items-center justify-between">
                <div className="text-sm text-gray-500">{role}</div>

                {/* acciones compactas */}
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => onToggleActive(user)}
                    title={user.is_active ? 'Desactivar usuario' : 'Activar usuario'}
                    aria-label={user.is_active ? `Desactivar ${user.username}` : `Activar ${user.username}`}
                    className="p-2 rounded hover:bg-gray-100"
                  >
                    {user.is_active ? <UserX className="w-5 h-5" /> : <UserCheck className="w-5 h-5" />}
                  </button>
                  <button onClick={() => onEditar(user)} title="Editar" aria-label={`Editar ${user.username}`} className="p-2 rounded hover:bg-gray-100">
                    <Edit className="w-5 h-5" />
                  </button>
                  <button onClick={() => onEliminar(user)} title="Eliminar" aria-label={`Eliminar ${user.username}`} className="p-2 rounded hover:bg-gray-100">
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </article>
          );
        })}
      </div>

      {/* DESKTOP: tabla */}
      <div className="hidden md:block overflow-x-auto bg-white rounded shadow">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50 sticky top-0">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Usuario</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rol</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Acciones</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {usuarios.map(usuario => {
              const role = usuario.role ?? usuario.rol ?? 'Cliente';
              const fullName = usuario.full_name ?? `${usuario.first_name} ${usuario.last_name}`.trim();
              return (
                <tr key={usuario.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="font-medium text-gray-900">{usuario.username}</div>
                    <div className="text-sm text-gray-500">{fullName}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{usuario.email}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{role}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${usuario.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      {usuario.is_active ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="inline-flex items-center gap-3">
                      <button
                        onClick={() => onToggleActive(usuario)}
                        title={usuario.is_active ? 'Desactivar' : 'Activar'}
                        aria-label={usuario.is_active ? `Desactivar ${usuario.username}` : `Activar ${usuario.username}`}
                      >
                        {usuario.is_active ? <UserX className="w-5 h-5" /> : <UserCheck className="w-5 h-5" />}
                      </button>

                      <button onClick={() => onEditar(usuario)} title="Editar usuario" aria-label={`Editar ${usuario.username}`}>
                        <Edit className="w-5 h-5" />
                      </button>

                      <button onClick={() => onEliminar(usuario)} title="Eliminar usuario" aria-label={`Eliminar ${usuario.username}`}>
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
