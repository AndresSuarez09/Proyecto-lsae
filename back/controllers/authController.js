const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const pool = require('../db');

// Mapeo: número → texto
function mapRoleNumberToText(roleNumber) {
  const roles = {
    1: 'gerente',
    2: 'jefe',
    3: 'rrhh',
    4: 'empleado'
  };
  return roles[parseInt(roleNumber)] || 'empleado';
}

// Mapeo: texto → número
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
// REGISTRO DE USUARIO
// -----------------------------
const registerUser = async (req, res) => {
  const { username, password, role, name } = req.body;

  try {
    const userExists = await pool.query('SELECT * FROM lae_user WHERE user_email = $1', [username]);
    if (userExists.rows.length > 0) {
      return res.status(400).json({ message: 'User already exists' });
    }

    const salt = await bcrypt.genSalt(10);
    const passwordHash = await bcrypt.hash(password, salt);

    const roleNumber = mapRoleTextToNumber(role);

    const newUser = await pool.query(
      'INSERT INTO lae_user (id_cargo, user_email, user_password, user_name) VALUES ($1, $2, $3, $4) RETURNING *',
      [roleNumber, username, passwordHash, name]
    );

    const payload = {
      user: {
        id: newUser.rows[0].id_user,
        role: mapRoleNumberToText(newUser.rows[0].id_cargo),
        user_name: newUser.rows[0].user_name
      }
    };

    jwt.sign(payload, process.env.JWT_SECRET, { expiresIn: '1h' }, (err, token) => {
      if (err) {
        console.error('Error al generar token:', err);
        return res.status(500).json({ message: 'No se pudo generar el token' });
      }
      return res.json({ token });
    });
  } catch (err) {
    console.error(err.message);
    return res.status(500).json({ message: 'Error interno del servidor' });
  }
};

// -----------------------------
// INICIO DE SESIÓN
// -----------------------------
const loginUser = async (req, res) => {
  const { username, password } = req.body;

  try {
    const user = await pool.query('SELECT * FROM lae_user WHERE user_email = $1', [username]);
    if (user.rows.length === 0) {
      return res.status(400).json({ message: `Usuario no encontrado: ${username}` });
    }

    const isMatch = await bcrypt.compare(password, user.rows[0].user_password);
    if (!isMatch) {
      return res.status(400).json({ message: 'Credenciales inválidas' });
    }

    const payload = {
      user: {
        id: user.rows[0].id_user,
        role: mapRoleNumberToText(user.rows[0].id_cargo),
        user_name: user.rows[0].user_name
      }
    };

    jwt.sign(payload, process.env.JWT_SECRET, { expiresIn: '1h' }, (err, token) => {
      if (err) {
        console.error('Error al generar token:', err);
        return res.status(500).json({ message: 'No se pudo generar el token' });
      }
      return res.json({ token });
    });
  } catch (err) {
    console.error(err.message);
    return res.status(500).json({ message: 'Error interno del servidor' });
  }
};

module.exports = {
  registerUser,
  loginUser
};
