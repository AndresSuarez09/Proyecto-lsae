// src/pages/Login.jsx
import { useState, useContext, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../utils/api';
import { AuthContext } from '../context/AuthContext';

export default function Login() {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [message, setMessage] = useState('');
  const navigate = useNavigate();
  const { setUserFromToken } = useContext(AuthContext);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        setUserFromToken(); // 🔄 reactiva el contexto por si quedó desincronizado
        navigate('/empleados');
      } catch (err) {
        console.warn('Token presente pero inválido. Sesión no restaurada.');
      }
    }
  }, []);

  const handleChange = e => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async e => {
    e.preventDefault();

    try {
      const res = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const { token, message: backendMessage } = res.data;

      if (typeof res.data === 'string' && res.data.startsWith('<!DOCTYPE')) {
        console.warn('⚠ El backend respondió con HTML en lugar de JSON');
        setMessage('Respuesta inesperada del servidor');
        return;
      }

      if (res.status === 200 && token) {
        localStorage.setItem('token', token);
        setUserFromToken();
        setMessage('✅ Inicio de sesión exitoso');
        navigate('/empleados');
      } else {
        setMessage(backendMessage || 'Error al iniciar sesión');
      }
    } catch (err) {
      console.error('❌ Error inesperado al conectar', err);
      setMessage('❌ Error de conexión con el servidor');
    }
  };

  return (
    <div>
      <h2>Iniciar Sesión</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Correo electrónico:</label>
          <input
            type="email"
            name="username"
            value={formData.username}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label>Contraseña:</label>
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
          />
        </div>
        <button type="submit">🔐 Iniciar Sesión</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
}
