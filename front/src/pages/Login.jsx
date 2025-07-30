// src/pages/Login.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../utils/api';

export default function Login() {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleChange = e => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async e => {
    e.preventDefault();

    try {
      const res = await api.post('/auth/login', formData);

      if (typeof res.data === 'string' && res.data.startsWith('<!DOCTYPE')) {
        console.warn('⚠ El backend respondió con HTML en lugar de JSON');
        setMessage('Respuesta inesperada del servidor');
        return;
      }

      const token = res.data.token;
      if (res.status === 200 && token) {
        localStorage.setItem('token', token);
        setMessage('✅ Inicio de sesión exitoso');
        navigate('/empleados'); // Redirección tras login
      } else {
        setMessage(res.data.message || 'Error al iniciar sesión');
      }
    } catch (err) {
      console.error(err);
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
