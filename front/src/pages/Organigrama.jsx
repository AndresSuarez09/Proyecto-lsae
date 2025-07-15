import { useState, useEffect } from 'react';
import { api } from '../utils/api';

export default function Organigrama() {
  const [empleados, setEmpleados] = useState([]);

  useEffect(() => {
    const token = localStorage.getItem('token');
    api.get('/orgchart', {
      headers: { Authorization: `Bearer ${token}` }
    })
    .then(res => setEmpleados(res.data))
    .catch(err => console.error('Error al cargar organigrama:', err));
  }, []);

  return (
    <div>
      <h3>📊 Organigrama de la empresa</h3>
      <table border="1" cellPadding="8" style={{ marginTop: '1rem', width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th>Empleado</th>
            <th>Cargo</th>
            <th>Jefe directo</th>
          </tr>
        </thead>
        <tbody>
          {empleados.map((emp) => (
            <tr key={emp.id}>
              <td>{emp.nombre}</td>
              <td>{emp.cargo}</td>
              <td>{emp.jefe || 'Sin jefe'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
