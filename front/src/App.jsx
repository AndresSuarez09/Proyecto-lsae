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

function App() {
  return (
    <>
      <Navbar />
      <main style={{ padding: '2rem' }}>
        <Routes>
          <Route path="/" element={<Login />} /> {/* ✅ Redirige a Login por defecto */}
          <Route path="/empleados" element={<Empleados />} /> {/* ✅ Ruta corregida */}
          <Route path="/empleados/:id/editar" element={<EditarEmpleado />} />
          <Route path="/register" element={<Register />} />
          <Route path="/certificates" element={<Certificates />} />
          <Route path="/solicitudes" element={<Solicitudes />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
    </>
  );
}

export default App;
