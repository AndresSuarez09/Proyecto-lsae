// src/App.jsx
import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Empleados from './pages/Empleados';
import Login from './pages/Login';
import Register from './pages/Register';
import Certificates from './pages/Certificates';
import NotFound from './pages/NotFound';
import Solicitudes from './pages/Solicitudes';
import EditarEmpleado from './pages/EditarEmpleado';
import ProtectedRoute from './utils/ProtectedRoute'; // ✅ Importamos el protector

function App() {
  return (
    <>
      <Navbar />
      <main style={{ padding: '2rem' }}>
        <Routes>
          <Route path="/" element={<Login />} /> {/* ✅ Página pública */}
          <Route path="/register" element={<Register />} />

          {/* 🔐 Rutas protegidas por login */}
          <Route path="/certificates" element={
            <ProtectedRoute><Certificates /></ProtectedRoute>
          } />
          <Route path="/empleados" element={
            <ProtectedRoute><Empleados /></ProtectedRoute>
          } />
          <Route path="/empleados/:id/editar" element={
            <ProtectedRoute><EditarEmpleado /></ProtectedRoute>
          } />
          <Route path="/solicitudes" element={
            <ProtectedRoute><Solicitudes /></ProtectedRoute>
          } />

          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
    </>
  );
}

export default App;
