// src/components/ListaEmpleados.jsx
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../utils/api';

export default function ListaEmpleados({ roleActual }) {
  const [lista, setLista] = useState([]);
  const token = localStorage.getItem('token');

  useEffect(() => {
    api
      .get('/users', {
        headers: { Authorization: `Bearer ${token}` }
      })
      .then((res) => setLista(res.data))
      .catch((err) => console.error('Error al cargar lista:', err));
  }, [token]);

  const eliminarEmpleado = (id) => {
    const confirmar = window.confirm('¿Estás seguro de que deseas eliminar este usuario?');
    if (!confirmar) return;

    api
      .delete(`/users/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      .then(() => {
        alert('Usuario eliminado con éxito');
        setLista(prev => prev.filter(item => item.id !== id));
      })
      .catch(err => {
        console.error(err);
        alert('Error al eliminar');
      });
  };

  return (
    <div>
      <h3>📋 Empleados registrados</h3>
      <table border="1" cellPadding="8" style={{ marginTop: '1rem', width: '100%' }}>
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Correo</th>
            <th>Departamento</th>
            <th>Rol</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {lista.map((empleado) => (
            <tr key={empleado.id}>
              <td>{empleado.nombre}</td>
              <td>{empleado.correo}</td>
              <td>{empleado.departamento}</td>
              <td>{empleado.rol}</td>
              <td>
                <Link to={`/empleados/${empleado.id}/editar`}>
                  <button>✏️ Editar</button>
                </Link>{' '}
                <button
                  onClick={() => eliminarEmpleado(empleado.id)}
                  disabled={roleActual !== 'admin' && roleActual !== 'rrhh'}
                  style={{
                    marginLeft: '0.5rem',
                    backgroundColor: '#ff4d4d',
                    color: 'white',
                    cursor: roleActual === 'admin' || roleActual === 'rrhh' ? 'pointer' : 'not-allowed'
                  }}
                >
                  🗑️ Eliminar
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
