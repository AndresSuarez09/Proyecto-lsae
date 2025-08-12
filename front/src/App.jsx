// src/utils/App.jsx
import { Routes, Route } from 'react-router-dom';
import Empleados from '../pages/Empleados';
import Login from '../pages/Login';
import Register from '../pages/Register';
import Certificates from '../pages/Certificates';
import NotFound from '../pages/NotFound';
import Solicitudes from '../pages/Solicitudes';
import EditarEmpleado from '../pages/EditarEmpleado';
import ProtectedRoute from './ProtectedRoute';
import Layout from '../components/Layout'; // ✅ nuevo import

function App() {
  return (
    <Routes>
      {/* Páginas públicas */}
      <Route path="/" element={<Login />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Páginas protegidas con Navbar activo */}
      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route path="/certificates" element={<Certificates />} />
        <Route path="/empleados" element={<Empleados />} />
        <Route path="/empleados/:id/editar" element={<EditarEmpleado />} />
        <Route path="/solicitudes" element={<Solicitudes />} />
      </Route>

      {/* Página de error */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

export default App;
