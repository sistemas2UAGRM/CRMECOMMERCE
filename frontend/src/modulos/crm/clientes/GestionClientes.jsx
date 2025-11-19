import React, { useState } from 'react';
import GestionClientesTable from './GestionClientesTable';
import GestionSegmentosTable from './GestionSegmentosTable';

const GestionClientes = () => {
  const [activeTab, setActiveTab] = useState('clientes');

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Gestión de Clientes</h1>
      <div className="flex border-b mb-4">
        <button
          className={`px-4 py-2 ${activeTab === 'clientes' ? 'border-b-2 border-blue-500' : ''}`}
          onClick={() => setActiveTab('clientes')}
        >
          Clientes
        </button>
        <button
          className={`px-4 py-2 ${activeTab === 'segmentos' ? 'border-b-2 border-blue-500' : ''}`}
          onClick={() => setActiveTab('segmentos')}
        >
          Segmentos
        </button>
      </div>
      {activeTab === 'clientes' && <GestionClientesTable />}
      {activeTab === 'segmentos' && <GestionSegmentosTable />}
    </div>
  );
};

export default GestionClientes;