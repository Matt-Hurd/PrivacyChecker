import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getChangeDetails } from './api';
import { Diff } from './types';

const DiffView: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [diff, setDiff] = useState<Diff | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDiff = async () => {
      if (!id) return; // Add this check
      setLoading(true);
      setError(null);
      try {
        const data = await getChangeDetails(id);
        setDiff(data);
      } catch (err) {
        setError('Failed to fetch diff. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchDiff();
  }, [id]);

  const renderDiff = () => {
    if (!diff || !diff.diff || !diff.diff.changed) return null;

    return Object.entries(diff.diff.changed).map(([key, changes]) => (
      <div key={key}>
        <h3>{key}</h3>
        <pre className="diff-content">
          {changes.map((change, index) => {
            if (change.type === 'added') {
              return <div key={index} style={{backgroundColor: '#e6ffed'}}>{`+ ${change.value}`}</div>;
            }
            if (change.type === 'removed') {
              return <div key={index} style={{backgroundColor: '#ffeef0'}}>{`- ${change.value}`}</div>;
            }
            if (change.type === 'replaced') {
              return (
                <React.Fragment key={index}>
                  <div style={{backgroundColor: '#ffeef0'}}>{`- ${change.old_value}`}</div>
                  <div style={{backgroundColor: '#e6ffed'}}>{`+ ${change.new_value}`}</div>
                </React.Fragment>
              );
            }
            return null;
          })}
        </pre>
      </div>
    ));
  };

  if (loading) return <p>Loading...</p>;
  if (error) return <p className="error">{error}</p>;
  if (!diff) return <p>No diff data available.</p>;

  return (
    <div className="diff-view">
      <h2>Diff View: {diff.from_version} → {diff.to_version}</h2>
      {renderDiff()}
    </div>
  );
};

export default DiffView;