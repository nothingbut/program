import React from 'react';
import { createRoot } from 'react-dom/client'; // Import createRoot from react-dom/client
import './index.css';

const App = () => (
  <div className="p-4">
    <h1 className="text-2xl font-bold">Welcome to Bookshelf</h1>
  </div>
);

// Use createRoot instead of ReactDOM.render
const container = document.getElementById('root');
if (container) {
  const root = createRoot(container);
  root.render(<App />);
}