// src/components/Navbar.jsx
import { useContext } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

export default function Navbar() {
  const { user, logout } = useContext(AuthContext);

  return (
    <nav style={styles.navbar}>
      <div style={styles.left}>
        <Link to="/empleados" style={styles.link}>Empleados</Link>
        <Link to="/" style={styles.link}>Login</Link>
        <Link to="/certificates" style={styles.link}>Certificates</Link>
        <Link to="/register" style={styles.link}>Register</Link>
        <Link to="/solicitudes" style={styles.link}>Solicitudes</Link>
      </div>

      {user && (
        <div style={styles.right}>
          <span style={styles.userInfo}>
            👤 {user.user_name} (<em>{user.role}</em>)
          </span>
          <button onClick={logout} style={styles.logoutBtn}>
            🔒 Cerrar sesión
          </button>
        </div>
      )}
    </nav>
  );
}

const styles = {
  navbar: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1rem',
    backgroundColor: '#f5f5f5',
    borderBottom: '1px solid #ccc',
    fontFamily: 'sans-serif',
  },
  left: {
    display: 'flex',
    gap: '1rem',
  },
  link: {
    textDecoration: 'none',
    color: '#333',
    fontWeight: 'bold',
  },
  right: {
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
  },
  userInfo: {
    fontStyle: 'italic',
    color: '#555',
  },
  logoutBtn: {
    backgroundColor: '#e74c3c',
    color: '#fff',
    border: 'none',
    padding: '6px 12px',
    borderRadius: '4px',
    cursor: 'pointer',
  },
};
