const pool = require('../db/pool');

const createUser = async (req, res) => {
  try {
    const {
      telefono_privado,
      correo_privado,
      cuenta_bancaria,
      contacto_emergencia,
      telefono_emergencia,
      nivel_estudio,
      anio_finalizacion,
      escuela,
      estado_civil,
      hijos_dependientes,
      nacionalidad,
      identificacion,
      pasaporte,
      genero,
      nacimiento_fecha,
      nacimiento_lugar
    } = req.body;

    const result = await pool.query(
      `INSERT INTO lae_user (
        telefono_privado, correo_privado, cuenta_bancaria, contacto_emergencia,
        telefono_emergencia, nivel_estudio, anio_finalizacion, escuela,
        estado_civil, hijos_dependientes, nacionalidad, identificacion,
        pasaporte, genero, nacimiento_fecha, nacimiento_lugar
      ) VALUES (
        $1, $2, $3, $4, $5, $6, $7, $8,
        $9, $10, $11, $12, $13, $14, $15, $16
      ) RETURNING id_user`,
      [
        telefono_privado || null,
        correo_privado || null,
        cuenta_bancaria || null,
        contacto_emergencia || null,
        telefono_emergencia || null,
        nivel_estudio || null,
        anio_finalizacion || null,
        escuela || null,
        estado_civil || null,
        parseInt(hijos_dependientes) || 0,
        nacionalidad || null,
        identificacion || null,
        pasaporte || null,
        genero || null,
        nacimiento_fecha || null,
        nacimiento_lugar || null
      ]
    );

    res.status(201).json({
      message: '✅ Usuario creado correctamente',
      id: result.rows[0].id_user
    });

  } catch (err) {
    console.error('❌ Error al crear usuario:', err.message);
    res.status(500).json({ message: 'Error al registrar usuario' });
  }
};

const getOwnProfile = async (req, res) => {
  const userId = req.user.id;
  try {
    const result = await pool.query(
      `SELECT * FROM lae_user WHERE id_user = $1`,
      [userId]
    );
    res.status(200).json(result.rows[0]);
  } catch (err) {
    console.error('❌ Error al obtener perfil:', err.message);
    res.status(500).json({ message: 'No se pudo obtener el perfil' });
  }
};

const updateOwnProfile = async (req, res) => {
  const userId = req.user.id;
  const fields = req.body;

  const keys = Object.keys(fields);
  const values = Object.values(fields);

  if (keys.length === 0) {
    return res.status(400).json({ message: 'No se recibieron datos para actualizar' });
  }

  const setClause = keys.map((key, index) => `${key} = $${index + 1}`).join(', ');

  try {
    await pool.query(
      `UPDATE lae_user SET ${setClause} WHERE id_user = $${keys.length + 1}`,
      [...values, userId]
    );
    res.status(200).json({ message: '✅ Perfil actualizado exitosamente' });
  } catch (err) {
    console.error('❌ Error al actualizar perfil:', err.message);
    res.status(500).json({ message: 'No se pudo actualizar el perfil' });
  }
};

const deleteOwnProfile = async (req, res) => {
  const userId = req.user.id;
  try {
    await pool.query(`DELETE FROM lae_user WHERE id_user = $1`, [userId]);
    res.status(200).json({ message: '🗑️ Usuario eliminado correctamente' });
  } catch (err) {
    console.error('❌ Error al eliminar usuario:', err.message);
    res.status(500).json({ message: 'No se pudo eliminar el usuario' });
  }
};

module.exports = {
  createUser,
  getOwnProfile,
  updateOwnProfile,
  deleteOwnProfile
};
