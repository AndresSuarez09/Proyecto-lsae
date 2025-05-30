const bcrypt = require('bcryptjs');
const pool = require('../db');

// Crear usuario (Gerente, Administrador o Empleado según permisos)
const createUser = async (req, res) => {
  const { username, password, role, name } = req.body;
  const creatorRole = req.user?.role;

  // Lógica de autorización personalizada
  const permisos = {
    1: [1, 2, 3], // Gerente puede crear todos
    2: [2, 3],    // Administrador puede crear admin y empleados
    3: [3],       // Empleado solo puede crear empleados
  };

  if (!permisos[creatorRole]?.includes(role)) {
    return res.status(403).json({
      message: 'No tienes permisos para crear este tipo de usuario',
    });
  }

  try {
    // Verificar si el usuario ya existe
    const userExists = await pool.query(
      'SELECT * FROM lae_user WHERE user_email = $1',
      [username]
    );
    if (userExists.rows.length > 0) {
      return res.status(400).json({ message: 'El usuario ya existe' });
    }

    // Hashear contraseña
    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(password, salt);

    // Insertar usuario
    const result = await pool.query(
      'INSERT INTO lae_user (user_name, user_email, user_password, id_cargo) VALUES ($1, $2, $3, $4) RETURNING *',
      [name, username, hashedPassword, role]
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

// Obtener perfil propio
const getOwnProfile = async (req, res) => {
  const userId = req.user?.id;

  try {
    const result = await pool.query(
      'SELECT user_name, user_email, id_cargo FROM lae_user WHERE id_user = $1',
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

module.exports = {
  createUser,
  getOwnProfile,
};
