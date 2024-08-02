import React from 'react';

interface FiltersProps {
  filters: {
    company: string;
    changeSize: string;
  };
  setFilters: React.Dispatch<React.SetStateAction<{
    company: string;
    changeSize: string;
  }>>;
}

const Filters: React.FC<FiltersProps> = ({ filters, setFilters }) => {
  const handleCompanyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFilters(prev => ({ ...prev, company: e.target.value }));
  };

  const handleChangeSizeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFilters(prev => ({ ...prev, changeSize: e.target.value }));
  };

  return (
    <div className="filters">
      <input
        type="text"
        placeholder="Filter by company"
        value={filters.company}
        onChange={handleCompanyChange}
      />
      <select value={filters.changeSize} onChange={handleChangeSizeChange}>
        <option value="">All sizes</option>
        <option value="small">Small (&lt;= 10 changes)</option>
        <option value="medium">Medium (11-50 changes)</option>
        <option value="large">Large (&gt; 50 changes)</option>
      </select>
    </div>
  );
};

export default Filters;