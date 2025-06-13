import { useState } from 'react';
import axios from 'axios';

export default function Empleados() {
  const [archivo, setArchivo] = useState(null);
  const [archivoSubido, setArchivoSubido] = useState(null);
  const [mensaje, setMensaje] = useState('');

  const handleArchivoChange = (e) => {
    setArchivo(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!archivo) {
      setMensaje('Por favor selecciona un archivo');
      return;
    }

    const formData = new FormData();
    formData.append('archivo', archivo);

    try {
      const res = await axios.post('https://proyecto-lsae-production.up.railway.app/api/files/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setArchivoSubido(res.data);
      setMensaje('Archivo subido correctamente');
    } catch (error) {
      console.error(error);
      setMensaje('Error al subir el archivo');
    }
  };

  return (
    <div>
      <h2>Gestión de Empleados - Subir Documentos</h2>

      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleArchivoChange} />
        <button type="submit">Subir Archivo</button>
      </form>

      {mensaje && <p>{mensaje}</p>}

      {archivoSubido && (
        <div>
          <p>Archivo disponible en:</p>
          <a
            href={`https://proyecto-lsae-production.up.railway.app/uploads/${archivoSubido.filename}`}
            target="_blank"
            rel="noopener noreferrer"
          >
            Descargar archivo
          </a>
        </div>
      )}
    </div>
  );
}
