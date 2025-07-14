import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';

export default function Navbar() {
  const navigate = useNavigate();
  const [decoded, setDecoded] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setDecoded(jwtDecode(token));
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <nav style={{ 
      display: 'flex', 
      justifyContent: 'space-between', 
      alignItems: 'center', 
      padding: '1rem', 
      background: '#eee',
      fontFamily: 'sans-serif'
    }}>
      <div>
        <Link to="/" style={{ marginRight: '1rem' }}>Empleados</Link>
        <Link to="/login" style={{ marginRight: '1rem' }}>Login</Link>
        <Link to="/certificates" style={{ marginRight: '1rem' }}>Certificates</Link>
        <Link to="/register" style={{ marginRight: '1rem' }}>Register</Link>
        <Link to="/solicitudes" style={{ marginRight: '1rem' }}>Solicitudes</Link>
      </div>
      {decoded && (
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <span style={{ marginRight: '1rem' }}>
            {decoded.user.user_name} (<em>{decoded.user.role}</em>)
          </span>
          <button onClick={handleLogout} style={{ padding: '6px 12px' }}>
            🔒 Cerrar sesión
          </button>
        </div>
      )}
    </nav>
  );
}
