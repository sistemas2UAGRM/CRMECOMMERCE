//frontend/src/modulos/usuarios/clientes/components/Profile.jsx

const Profile = () => {
  return (
    <div className="bg-white p-8 rounded-lg shadow-md">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">Mi Perfil</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-gray-600 mb-2">Nombre Completo</label>
          <input type="text" value="Edixon Apaza" className="w-full p-2 border rounded-md" disabled />
        </div>
        <div>
          <label className="block text-gray-600 mb-2">Correo Electrónico</label>
          <input type="email" value="edixon.apaza@example.com" className="w-full p-2 border rounded-md" disabled />
        </div>
        <div>
          <label className="block text-gray-600 mb-2">Dirección de Envío</label>
          <input type="text" value="Av. Siempre Viva 123" className="w-full p-2 border rounded-md" />
        </div>
        <div>
          <label className="block text-gray-600 mb-2">Teléfono</label>
          <input type="tel" value="+591 123 45678" className="w-full p-2 border rounded-md" />
        </div>
      </div>
      <button className="mt-8 bg-blue-600 text-white py-2 px-6 rounded-md hover:bg-blue-700 transition-colors">
        Guardar Cambios
      </button>
    </div>
  );
};

export default Profile;