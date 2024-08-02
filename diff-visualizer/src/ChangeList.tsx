import React, { useState, useEffect } from 'react';
import ChangeItem from './ChangeItem';
import Filters from './Filters';
import { getChanges } from './api';
import { Diff } from './types';

const ChangeList: React.FC = () => {
  const [changes, setChanges] = useState<Diff[]>([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState({
    company: '',
    changeSize: ''
  });

  useEffect(() => {
    const fetchChanges = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getChanges({
          page,
          limit: 20,
          company: filters.company,
          changeSize: filters.changeSize,
        });
        setChanges(data.changes);
      } catch (err) {
        setError('Failed to fetch changes. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchChanges();
  }, [filters, page]);

  const loadMore = () => {
    setPage(prevPage => prevPage + 1);
  };

  return (
    <div className="change-list">
      <Filters filters={filters} setFilters={setFilters} />
      {changes.map((change, index) => (
        <ChangeItem key={change.id || index} change={change} />
      ))}
      {loading && <p>Loading...</p>}
      {error && <p className="error">{error}</p>}
      {!loading && !error && changes.length > 0 && (
        <button onClick={loadMore}>
          Load More
        </button>
      )}
    </div>
  );
};

export default ChangeList;