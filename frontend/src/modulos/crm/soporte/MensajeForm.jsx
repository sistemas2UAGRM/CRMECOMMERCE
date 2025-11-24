import React, { useState } from 'react';

const MensajeForm = ({ onSave, onCancel }) => {
  const [mensaje, setMensaje] = useState('');
  const [adjunto, setAdjunto] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    const data = { mensaje, adjunto };
    onSave(data);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Mensaje</label>
        <textarea
          value={mensaje}
          onChange={(e) => setMensaje(e.target.value)}
          className="w-full border px-3 py-2 rounded"
          required
        />
      </div>
      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Adjunto</label>
        <input
          type="file"
          onChange={(e) => setAdjunto(e.target.files[0])}
          className="w-full border px-3 py-2 rounded"
        />
      </div>
      <div className="flex justify-end gap-2">
        <button type="button" onClick={onCancel} className="px-4 py-2 bg-gray-300 rounded">Cancelar</button>
        <button type="submit" className="px-4 py-2 bg-blue-500 text-white rounded">Enviar</button>
      </div>
    </form>
  );
};

export default MensajeForm;