import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import ChangeList from './ChangeList';
import DiffView from './DiffView';

const App: React.FC = () => {
  return (
    <Router>
      <div className="App">
        <h1>Privacy Policy Change Tracker</h1>
        <Routes>
          <Route path="/" element={<ChangeList />} />
          <Route path="/diff/:id" element={<DiffView />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;