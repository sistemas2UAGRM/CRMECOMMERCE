// src/modulos/usuarios/admin/UserTable.jsx
import React from 'react';
import { Edit, Trash2, UserCheck, UserX } from 'lucide-react';

export default function UserTable({ usuarios = [], onEditar, onEliminar, onToggleActive }) {
  if (!usuarios) return null;

  return (
    <div className="space-y-4">
      {/* --- MOBILE: Cards --- */}
      <div className="grid grid-cols-1 gap-4 md:hidden">
        {usuarios.map(user => (
          <div key={user.id} className="bg-white p-4 rounded-lg shadow hover:shadow-lg transition-shadow">
            <div className="flex items-start justify-between">
              <div>
                <div className="font-semibold text-gray-900">{user.username}</div>
                <div className="text-sm text-gray-500">{user.first_name} {user.last_name}</div>
                <div className="text-sm text-gray-500">{user.email}</div>
              </div>
              <div className="text-right">
                <div className="text-xs font-medium">
                  <span className={`px-2 py-1 rounded-full text-xs ${user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                    {user.is_active ? 'Activo' : 'Inactivo'}
                  </span>
                </div>
              </div>
            </div>

            <div className="mt-3 flex items-center justify-between">
              <div className="text-sm text-gray-500">{user.rol || 'Cliente'}</div>
              <div className="flex items-center gap-2">
                <button onClick={() => onToggleActive(user)} className="p-2 rounded hover:bg-gray-100">
                  {user.is_active ? <UserX className="w-5 h-5"/> : <UserCheck className="w-5 h-5"/>}
                </button>
                <button onClick={() => onEditar(user)} className="p-2 rounded hover:bg-gray-100"><Edit className="w-5 h-5" /></button>
                <button onClick={() => onEliminar(user)} className="p-2 rounded hover:bg-gray-100"><Trash2 className="w-5 h-5" /></button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* --- DESKTOP: Tabla --- */}
      <div className="hidden md:block overflow-x-auto bg-white rounded shadow">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Usuario</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rol</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Acciones</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {usuarios.map((usuario) => (
              <tr key={usuario.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="font-medium text-gray-900">{usuario.username}</div>
                  <div className="text-sm text-gray-500">{usuario.first_name} {usuario.last_name}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{usuario.email}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{usuario.rol || 'Cliente'}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${usuario.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                    {usuario.is_active ? 'Activo' : 'Inactivo'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                  <button onClick={() => onToggleActive(usuario)} title={usuario.is_active ? 'Desactivar' : 'Activar'}>
                    {usuario.is_active ? <UserX className="w-5 h-5 text-yellow-600"/> : <UserCheck className="w-5 h-5 text-green-600"/>}
                  </button>
                  <button onClick={() => onEditar(usuario)}><Edit className="w-5 h-5 text-blue-600" /></button>
                  <button onClick={() => onEliminar(usuario)}><Trash2 className="w-5 h-5 text-red-600" /></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
