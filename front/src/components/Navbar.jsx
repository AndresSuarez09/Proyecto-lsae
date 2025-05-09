// src/components/Navbar.jsx
import { Link } from 'react-router-dom';

export default function Navbar() {
  return (
    <nav style={{ padding: '1rem', background: '#eee' }}>
      {/* Test with inline styles first */}
      <Link to="/" style={{ marginRight: '1rem' }}>Empleados</Link>
      <Link to="/login" style={{ marginRight: '1rem' }}>Login</Link>
      <Link to="/certificates" style={{ marginRight: '1rem' }}>Certificates</Link> 
      <Link to="/register" style={{ marginRight: '1rem' }}>Register</Link>
      <Link to="/solicitudes" style={{ marginRight: '1rem' }}>Solicitudes</Link>
    </nav>
  );
}