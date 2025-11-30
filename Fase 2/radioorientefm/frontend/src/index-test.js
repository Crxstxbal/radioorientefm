import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import TestComponent from './TestComponent';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <TestComponent />
  </React.StrictMode>
);
