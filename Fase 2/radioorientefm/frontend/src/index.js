import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { AuthProvider } from './contexts/AuthContext';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>

    <AuthProvider>
      <App />
      </AuthProvider>
  </React.StrictMode>
);

//if you want to start measuring performance in your app, pass a function
//to log results (for example: reportwebvitals(console.log))
//or send to an analytics endpoint. learn more: https://bit.ly/cra-vitals
reportWebVitals();
