import React from 'react';
import { Search, Filter } from 'lucide-react';

const CrmFilters = ({ filters, onFilterChange, placeholder = "Buscar..." }) => {
  const handleChange = (key, value) => {
    onFilterChange({ ...filters, [key]: value });
  };

  return (
    <div className="flex flex-wrap gap-4 mb-4">
      <div className="flex items-center border rounded-lg px-3 py-2">
        <Search size={16} className="text-gray-500 mr-2" />
        <input
          type="text"
          placeholder={placeholder}
          value={filters.search || ''}
          onChange={(e) => handleChange('search', e.target.value)}
          className="outline-none"
        />
      </div>
      {/* Add more filters as needed, e.g., date pickers, selects */}
    </div>
  );
};

export default CrmFilters;