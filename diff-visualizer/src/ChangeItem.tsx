import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Diff } from './types';
import { getChangeDetails } from './api';

interface ChangeItemProps {
  change: Diff;
}

const ChangeItem: React.FC<ChangeItemProps> = ({ change }) => {
  const [expanded, setExpanded] = useState(false);
  const [details, setDetails] = useState<Diff | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const toggleExpanded = async () => {
    if (!expanded && !details) {
      setLoading(true);
      setError(null);
      try {
        const detailedChange = await getChangeDetails(change.id);
        setDetails(detailedChange);
      } catch (err) {
        setError('Failed to fetch change details. Please try again.');
      } finally {
        setLoading(false);
      }
    }
    setExpanded(!expanded);
  };

  const renderTextChanges = () => {
    if (!details || !details.diff || !details.diff.changed) return null;

    return Object.entries(details.diff.changed)
      .filter(([key]) => key.endsWith('.text'))
      .map(([key, changes]) => (
        <div key={key}>
          <h4>{key}</h4>
          <ul>
            {changes.map((change, index) => (
              <li key={index}>
                {change.type === 'added' && <span style={{color: 'green'}}>Added: {change.value}</span>}
                {change.type === 'removed' && <span style={{color: 'red'}}>Removed: {change.value}</span>}
                {change.type === 'replaced' && (
                  <span>
                    Replaced: <span style={{color: 'red'}}>{change.old_value}</span> with{' '}
                    <span style={{color: 'green'}}>{change.new_value}</span>
                  </span>
                )}
              </li>
            ))}
          </ul>
        </div>
      ));
  };

  return (
    <div className="change-item">
      <h3 onClick={toggleExpanded}>{change.company}: {change.from_version} → {change.to_version}</h3>
      <p>Total changes: {change.summary.total_changes}</p>
      {expanded && (
        <div className="change-details">
          {loading && <p>Loading details...</p>}
          {error && <p className="error">{error}</p>}
          {details && (
            <>
              <p>Added: {details.summary.added}</p>
              <p>Removed: {details.summary.removed}</p>
              <p>Changed: {details.summary.changed}</p>
              <p>Type changes: {details.summary.type_changes}</p>
              <h4>Text Changes:</h4>
              {renderTextChanges()}
              <Link to={`/diff/${change.id}`}>
                <button>View entire diff</button>
              </Link>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default ChangeItem;