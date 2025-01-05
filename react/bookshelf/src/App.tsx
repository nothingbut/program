import React from 'react';
import Bookshelf from './components/Bookshelf';

const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-100">
      <Bookshelf />
    </div>
  );
};

export default App;