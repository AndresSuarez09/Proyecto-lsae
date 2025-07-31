import { useState, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';
import Curriculo from './Curriculo';
import InformacionPrivada from './InformacionPrivada';
import Organigrama from './Organigrama';
import ListaEmpleados from '../components/ListaEmpleados';
import { api } from '../utils/api';

export default function Empleados() {
  const [activeTab, setActiveTab] = useState('curriculo');
  const [profile, setProfile] = useState({});
  const [role, setRole] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      const decoded = jwtDecode(token);
      setRole(decoded.user.role);
      getProfile(token);
    }
  }, []);

  const getProfile = async (token) => {
    try {
      const res = await api.get('/users/me', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProfile(res.data);
    } catch (err) {
      console.error('Error al cargar perfil:', err);
    }
  };

  return (
    <div style={{ padding: '2rem' }}>
      <h2>👤 Información general del empleado</h2>
      <p><strong>Nombre:</strong> {profile.user_name}</p>
      <p><strong>Correo:</strong> {profile.user_email}</p>
      <p><strong>Cargo:</strong> {role}</p>
      <p><strong>Teléfono empresa:</strong> {profile.telefono_empresa || 'No asignado'}</p>
      <p><strong>Departamento:</strong> {profile.departamento || 'Sin departamento'}</p>
      <p><strong>Jefe:</strong> {profile.jefe_nombre || 'No asignado'}</p>

      <hr />

      <div>
        <button onClick={() => setActiveTab('curriculo')}>📁 Currículo</button>
        <button onClick={() => setActiveTab('privada')}>🔒 Información Privada</button>
        <button onClick={() => setActiveTab('organigrama')}>📊 Organigrama</button>
        <button onClick={() => setActiveTab('lista')}>📋 Lista de Empleados</button>
      </div>

      <div style={{ marginTop: '2rem' }}>
        {activeTab === 'curriculo' && <Curriculo />}
        {activeTab === 'privada' && <InformacionPrivada role={role} />}
        {activeTab === 'organigrama' && <Organigrama />}
        {activeTab === 'lista' && <ListaEmpleados roleActual={role} />}
      </div>
    </div>
  );
}
