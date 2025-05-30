const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const pool = require('../db');

// -----------------------------
// REGISTRO DE USUARIO
// -----------------------------
const registerUser = async (req, res) => {
    const { username, password, role, name } = req.body;

    try {
        // [ANTES] Verificaba si el usuario ya existía
        const userExists = await pool.query('SELECT * FROM lae_user WHERE user_email = $1', [username]);
        if (userExists.rows.length > 0) {
            return res.status(400).json({ message: 'User already exists' });
        }

        // [ANTES] Hash de la contraseña
        const salt = await bcrypt.genSalt(10);
        const passwordHash = await bcrypt.hash(password, salt);

        // [ANTES] Insertar el usuario con id_cargo como "role"
        // [DESPUÉS] Asegurarse de que se guarda correctamente
        const newUser = await pool.query(
            'INSERT INTO lae_user (id_cargo, user_email, user_password, user_name) VALUES ($1, $2, $3, $4) RETURNING *',
            [role, username, passwordHash, name]
        );

        // [ANTES] Generaba el JWT solo con el id
        // [DESPUÉS] Incluye el rol también en el token
        const payload = {
            user: {
                id: newUser.rows[0].id_user,
                role: newUser.rows[0].id_cargo, // <- corregido aquí
            },
        };

        jwt.sign(
            payload,
            process.env.JWT_SECRET,
            { expiresIn: '1h' },
            (err, token) => {
                if (err) throw err;
                res.json({ token });
            }
        );
    } catch (err) {
        console.error(err.message);
        res.status(500).send('Server error');
    }
};

// -----------------------------
// INICIO DE SESIÓN
// -----------------------------
const loginUser = async (req, res) => {
    const { username, password } = req.body;

    try {
        // [ANTES] Verificaba existencia del usuario
        const user = await pool.query('SELECT * FROM lae_user WHERE user_email = $1', [username]);
        if (user.rows.length === 0) {
            return res.status(400).json({ message: 'Usuario no encontrado: ' + username });
        }

        // [ANTES] Comparaba la contraseña con bcrypt
        const isMatch = await bcrypt.compare(password, user.rows[0].user_password);
        if (!isMatch) {
            return res.status(400).json({ message: 'Credenciales inválidas' });
        }

        // [ANTES] JWT solo contenía ID
        // [DESPUÉS] Incluye el rol del usuario
        const payload = {
            user: {
                id: user.rows[0].id_user,
                role: user.rows[0].id_cargo, // <- asegúrate que sea el nombre del campo de rol
            },
        };

        jwt.sign(
            payload,
            process.env.JWT_SECRET,
            { expiresIn: '1h' },
            (err, token) => {
                if (err) throw err;
                res.json({ token });
            }
        );
    } catch (err) {
        console.error(err.message);
        res.status(500).send('Server error');
    }
};

// -----------------------------
// EXPORTACIÓN
// -----------------------------
module.exports = {
    registerUser,
    loginUser
};
