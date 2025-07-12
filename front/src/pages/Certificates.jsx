import { useState } from 'react';
import { api } from '../utils/api';
import { jwtDecode } from 'jwt-decode'; 


export default function Certificates() {
  const [message, setMessage] = useState('');

  const handleDownload = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      setMessage('Sesión expirada. Inicia sesión de nuevo.');
      return;
    }

    const decoded = jwtDecode(token);
    const userId = decoded.user.id;

    try {
      const res = await api.get(`/certificados/${userId}`, {
        responseType: 'blob',
      });

      const blob = new Blob([res.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `certificado_${userId}.pdf`);
      document.body.appendChild(link);
      link.click();

      setMessage('✅ Certificado descargado con éxito');
    } catch (err) {
      console.error(err);
      setMessage('❌ Error al generar el certificado');
    }
  };

  return (
    <div>
      <h1>Certificados</h1>
      <p>Haz clic para generar tu certificado laboral personalizado:</p>
      <button onClick={handleDownload}>📄 Descargar certificado</button>
      {message && <p>{message}</p>}
    </div>
  );
}
