// frontend/src/components/MenuHorizontal.jsx
import React from 'react';

// Recibe los items, el item activo actual y una función para cambiarlo
const MenuHorizontal = ({ items, activeSubItem, onSubItemClick }) => {
  if (!items || items.length === 0) {
    return null; // No renderiza nada si no hay items
  }

  return (
    <nav className="border-b border-gray-200 bg-white">
      <ul className="flex -mb-px px-6 lg:px-8">
        {items.map((item) => {
          const isActive = activeSubItem && activeSubItem.name === item.name;
          return (
            <li key={item.name} className="mr-2">
              <button
                onClick={() => onSubItemClick(item)}
                className={`inline-block p-4 text-sm font-medium text-center border-b-2 transition-colors duration-200
                  ${
                    isActive
                      ? 'border-cyan-500 text-cyan-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                {item.name}
              </button>
            </li>
          );
        })}
      </ul>
    </nav>
  );
};

export default MenuHorizontal;