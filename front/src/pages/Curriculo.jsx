import { useState } from 'react';
import axios from 'axios';

export default function Curriculo() {
  const [archivo, setArchivo] = useState(null);
  const [mensaje, setMensaje] = useState('');
  const [archivoSubido, setArchivoSubido] = useState(null);

  const handleArchivoChange = (e) => {
    setArchivo(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!archivo) return setMensaje('Selecciona un archivo');

    const formData = new FormData();
    formData.append('archivo', archivo);

    try {
      const res = await axios.post('https://proyecto-lsae-production.up.railway.app/api/files/upload', formData);
      setArchivoSubido(res.data);
      setMensaje('Archivo subido correctamente');
    } catch (err) {
      console.error(err);
      setMensaje('Error al subir el archivo');
    }
  };

  return (
    <div>
      <h3>📎 Subir Hoja de Vida</h3>
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleArchivoChange} />
        <button type="submit">Subir</button>
      </form>
      {mensaje && <p>{mensaje}</p>}
      {archivoSubido && (
        <p>
          📄 <a href={`https://proyecto-lsae-production.up.railway.app/uploads/${archivoSubido.filename}`} target="_blank" rel="noopener noreferrer">Descargar CV</a>
        </p>
      )}
    </div>
  );
}
