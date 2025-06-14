import { useNavigate } from 'react-router-dom';
import axios from 'axios';

export default function useAuth() {
  const navigate = useNavigate();

  const login = async (email, password) => {
    try {
      const res = await axios.post('https://proyecto-lsae-production.up.railway.app/api/auth/login', { email, password });

      if (res.status === 200) {
        localStorage.setItem('token', res.data.token);
        navigate('/certificates'); // O la ruta que desees después del login
      } else {
        console.error('Error en el login', res.data.message);
      }
    } catch (error) {
      console.error('Error al conectar con el servidor', error);
    }
  };

  return { login };
}
