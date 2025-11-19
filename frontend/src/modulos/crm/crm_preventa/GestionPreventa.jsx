import React, { useState } from 'react';
import GestionPotenciales from './GestionPotenciales';
import GestionContactos from './GestionContactos';
import GestionOportunidades from './GestionOportunidades';
import GestionActividades from './GestionActividades';

const GestionPreventa = () => {
  const [activeTab, setActiveTab] = useState('potenciales');

  const tabs = [
    { key: 'potenciales', label: 'Potenciales', component: <GestionPotenciales /> },
    { key: 'contactos', label: 'Contactos', component: <GestionContactos /> },
    { key: 'oportunidades', label: 'Oportunidades', component: <GestionOportunidades /> },
    { key: 'actividades', label: 'Actividades', component: <GestionActividades /> },
  ];

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Gestión de Preventa</h1>
      <div className="flex border-b mb-4">
        {tabs.map(tab => (
          <button
            key={tab.key}
            className={`px-4 py-2 ${activeTab === tab.key ? 'border-b-2 border-blue-500' : ''}`}
            onClick={() => setActiveTab(tab.key)}
          >
            {tab.label}
          </button>
        ))}
      </div>
      {tabs.find(tab => tab.key === activeTab)?.component}
    </div>
  );
};

export default GestionPreventa;