const bcrypt = require('bcryptjs');
const pool = require('../db');

// 🔁 Mapeo texto → número
function mapRoleTextToNumber(roleText) {
  const roles = {
    gerente: 1,
    jefe: 2,
    rrhh: 3,
    empleado: 4
  };
  return roles[roleText] || 4;
}

// -----------------------------
// Crear usuario con jerarquía
// -----------------------------
const createUser = async (req, res) => {
  const { username, password, role, name } = req.body;
  const creatorRole = req.user?.role;

  const permisos = {
    gerente: ['gerente', 'jefe', 'rrhh'],
    jefe: ['jefe', 'rrhh'],
    rrhh: ['rrhh']
  };

  if (!permisos[creatorRole]?.includes(role)) {
    return res.status(403).json({
      message: 'No tienes permisos para crear este tipo de usuario',
    });
  }

  try {
    const userExists = await pool.query(
      'SELECT * FROM lae_user WHERE user_email = $1',
      [username]
    );
    if (userExists.rows.length > 0) {
      return res.status(400).json({ message: 'El usuario ya existe' });
    }

    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(password, salt);
    const roleNumber = mapRoleTextToNumber(role);

    const result = await pool.query(
      'INSERT INTO lae_user (user_name, user_email, user_password, id_cargo) VALUES ($1, $2, $3, $4) RETURNING *',
      [name, username, hashedPassword, roleNumber]
    );

    res.status(201).json({
      message: 'Usuario creado correctamente',
      user: result.rows[0],
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Error en el servidor' });
  }
};

// -----------------------------
// Obtener perfil propio
// -----------------------------
const getOwnProfile = async (req, res) => {
  const userId = req.user?.id;

  try {
    const result = await pool.query(
      'SELECT * FROM lae_user WHERE id_user = $1',
      [userId]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Usuario no encontrado' });
    }

    res.json(result.rows[0]);
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Error al obtener perfil' });
  }
};

// -----------------------------
// Actualizar perfil privado
// -----------------------------
const updateOwnProfile = async (req, res) => {
  const userId = req.user?.id;
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

  try {
    await pool.query(
      `UPDATE lae_user SET
        telefono_privado = $1,
        correo_privado = $2,
        cuenta_bancaria = $3,
        contacto_emergencia = $4,
        telefono_emergencia = $5,
        nivel_estudio = $6,
        anio_finalizacion = $7,
        escuela = $8,
        estado_civil = $9,
        hijos_dependientes = $10,
        nacionalidad = $11,
        identificacion = $12,
        pasaporte = $13,
        genero = $14,
        nacimiento_fecha = $15,
        nacimiento_lugar = $16
      WHERE id_user = $17`,
      [
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
        nacimiento_lugar,
        userId
      ]
    );

    res.json({ message: '✅ Perfil actualizado correctamente' });
  } catch (err) {
    console.error('Error al actualizar perfil:', err);
    res.status(500).json({ message: 'Error en el servidor al actualizar perfil' });
  }
};

// -----------------------------
module.exports = {
  createUser,
  getOwnProfile,
  updateOwnProfile
};
