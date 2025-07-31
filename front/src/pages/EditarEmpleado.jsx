import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../utils/api';

function EditarEmpleado() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [datos, setDatos] = useState({});
  const [mensaje, setMensaje] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('token');
    api.get(`/users/${id}`, {
      headers: { Authorization: `Bearer ${token}` }
    }).then(res => setDatos(res.data))
      .catch(err => {
        console.error(err);
        setMensaje('❌ Error al cargar datos del usuario');
      });
  }, [id]);

  const handleChange = (e) => {
    setDatos({ ...datos, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem('token');
    try {
      await api.put(`/users/${id}`, datos, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMensaje('✅ Usuario actualizado');
      setTimeout(() => navigate('/empleados'), 2000);
    } catch (err) {
      console.error(err);
      setMensaje('❌ Error al actualizar usuario');
    }
  };

  return (
    <div style={{ padding: '2rem' }}>
      <h2>✏️ Editar empleado</h2>
      {mensaje && <p><strong>{mensaje}</strong></p>}
      <form onSubmit={handleSubmit}>
        <label>
          Nombre:
          <input name="user_name" value={datos.user_name || ''} onChange={handleChange} />
        </label>
        <br />
        <label>
          Correo:
          <input name="user_email" value={datos.user_email || ''} onChange={handleChange} />
        </label>
        <br />
        <label>
          Departamento:
          <input name="departamento" value={datos.departamento || ''} onChange={handleChange} />
        </label>
        <br />
        <button type="submit">💾 Guardar cambios</button>
      </form>
    </div>
  );
}

export default EditarEmpleado;
