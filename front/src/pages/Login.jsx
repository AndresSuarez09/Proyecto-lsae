import { useState } from 'react';
import { api } from '../../utils/api'; // Ruta corregida

export default function Login() {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });

  const [message, setMessage] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const res = await api.post('/auth/login', formData);

      if (res.status === 200) {
        localStorage.setItem('token', res.data.token);
        setMessage('Inicio de sesión exitoso');
        // Si quieres redirigir:
        // window.location.href = '/empleados';
      } else {
        setMessage(res.data.message || 'Error al iniciar sesión');
      }
    } catch (err) {
      console.error(err);
      setMessage('Error de conexión con el servidor');
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
        <button type="submit">Iniciar Sesión</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
}
