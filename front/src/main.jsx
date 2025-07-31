import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import { AuthProvider } from './context/AuthContext'; // ✅ Nuevo

const container = document.getElementById('root');
const root = createRoot(container);

root.render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider> {/* ✅ Envuelve la app */}
        <App />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
