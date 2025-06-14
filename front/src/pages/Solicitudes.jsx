// src/pages/Solicitudes.jsx
import { useState, useEffect } from 'react';

export default function Solicitudes() {
  const [formData, setFormData] = useState({
    empleado_id: '',
    tipo_solicitud: '',
    descripcion: '',
  });
  const [message, setMessage] = useState('');

  const handleChange = e => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async e => {
    e.preventDefault();
    try {
      const res = await fetch('https://proyecto-lsae-production.up.railway.app/api/solicitudes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      const data = await res.json();
      if (res.ok) {
        setMessage(`Solicitud creada (ID: ${data.solicitud.id_solicitud})`);
        setFormData({ empleado_id: '', tipo_solicitud: '', descripcion: '' });
      } else {
        setMessage(data.error || 'Error al crear solicitud');
      }
    } catch (err) {
      console.error(err);
      setMessage('Error de conexión al servidor');
    }
  };

  return (
    <div className="max-w-md mx-auto p-4">
      <h2 className="text-xl font-bold mb-4">Nueva Solicitud</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block mb-1">ID Empleado:</label>
          <input
            type="number"
            name="empleado_id"
            value={formData.empleado_id}
            onChange={handleChange}
            required
            className="w-full p-2 border rounded"
          />
        </div>
        <div>
          <label className="block mb-1">Tipo de Solicitud:</label>
          <input
            type="text"
            name="tipo_solicitud"
            value={formData.tipo_solicitud}
            onChange={handleChange}
            required
            className="w-full p-2 border rounded"
          />
        </div>
        <div>
          <label className="block mb-1">Descripción:</label>
          <textarea
            name="descripcion"
            value={formData.descripcion}
            onChange={handleChange}
            required
            className="w-full p-2 border rounded"
          />
        </div>
        <button
          type="submit"
          className="w-full py-2 bg-blue-600 text-white rounded"
        >
          Crear Solicitud
        </button>
      </form>
      {message && <p className="mt-4">{message}</p>}
    </div>
  );
}
