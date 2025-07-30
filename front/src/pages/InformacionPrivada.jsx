import { useState, useEffect } from 'react';
import jwtDecode from 'jwt-decode';
import { api } from '../utils/api';

export default function InformacionPrivada({ role }) {
  const [datos, setDatos] = useState({});
  const [mensaje, setMensaje] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('token');
    api.get('/users/me', {
      headers: { Authorization: `Bearer ${token}` }
    }).then(res => setDatos(res.data));
  }, []);

  const handleChange = (e) => {
    setDatos({ ...datos, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem('token');
    try {
      await api.put('/users/me/update', datos, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMensaje('✅ Datos actualizados correctamente');
    } catch (err) {
      console.error(err);
      setMensaje('Error al actualizar');
    }
  };

  const puedeEditar = ['gerente', 'jefe', 'rrhh'].includes(role);

  return (
    <form onSubmit={handleSubmit}>
      <fieldset disabled={!puedeEditar}>
        <h4>📱 Contacto Privado</h4>
        <input name="telefono_privado" placeholder="Teléfono" value={datos.telefono_privado || ''} onChange={handleChange} />
        <input name="correo_privado" placeholder="Correo" value={datos.correo_privado || ''} onChange={handleChange} />
        <input name="cuenta_bancaria" placeholder="Cuenta Bancaria" value={datos.cuenta_bancaria || ''} onChange={handleChange} />

        <h4>🚨 Emergencia</h4>
        <input name="contacto_emergencia" placeholder="Nombre contacto" value={datos.contacto_emergencia || ''} onChange={handleChange} />
        <input name="telefono_emergencia" placeholder="Teléfono contacto" value={datos.telefono_emergencia || ''} onChange={handleChange} />

        <h4>🎓 Educación</h4>
        <input name="nivel_estudio" placeholder="Nivel" value={datos.nivel_estudio || ''} onChange={handleChange} />
        <input name="anio_finalizacion" placeholder="Año de finalización" value={datos.anio_finalizacion || ''} onChange={handleChange} />
        <input name="escuela" placeholder="Escuela" value={datos.escuela || ''} onChange={handleChange} />

        <h4>👪 Situación Familiar</h4>
        <input name="estado_civil" placeholder="Estado civil" value={datos.estado_civil || ''} onChange={handleChange} />
        <input name="hijos_dependientes" placeholder="Cantidad hijos" value={datos.hijos_dependientes || ''} onChange={handleChange} />

        <h4>🌐 Nacionalidad</h4>
        <input name="nacionalidad" placeholder="País" value={datos.nacionalidad || ''} onChange={handleChange} />
        <input name="identificacion" placeholder="Número identificación" value={datos.identificacion || ''} onChange={handleChange} />
        <input name="pasaporte" placeholder="Pasaporte" value={datos.pasaporte || ''} onChange={handleChange} />
        <input name="genero" placeholder="Género" value={datos.genero || ''} onChange={handleChange} />
        <input name="nacimiento_fecha" placeholder="Fecha nacimiento" value={datos.nacimiento_fecha || ''} onChange={handleChange} />
        <input name="nacimiento_lugar" placeholder="Lugar nacimiento" value={datos.nacimiento_lugar || ''} onChange={handleChange} />
      </fieldset>
      {puedeEditar && <button type="submit">Guardar Cambios</button>}
      {mensaje && <p>{mensaje}</p>}
    </form>
  );
}
