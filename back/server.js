require('dotenv').config();
const express = require('express');
const cors = require('cors');
const pool = require('./db'); // Tu conexión PostgreSQL
const authRoutes = require('./routes/authRoutes'); // Rutas de autenticación
const solicitudesRoutes = require('./routes/solicitudesRoutes'); // Rutas de solicitudes
const fileRoutes = require('./routes/fileRoutes'); // Carga y descarga archivos
const userRoutes = require('./routes/userRoutes'); // Rutas para usuarios: crear/ver perfil

const app = express();
const port = process.env.PORT || 3001;
const path = require('path');

// 1) Middlewares
app.use(express.static(path.join(__dirname, 'public')));//29demayo

app.use(cors()); // Permite peticiones desde cualquier origen
app.use(express.json()); // Para entender JSON en los cuerpos de petición
//app.use(express.static('public')); // Sirve forms.html desde back/public
app.use(express.static(path.join(__dirname, '../front/public')));
app.use('/uploads', express.static(path.join(__dirname, 'uploads'))); // Para servir archivos subidos

app.use('/test', express.static(path.join(__dirname, 'web-test'))); //prueba29mayo


// 2) Registrar rutas
app.use('/api/auth', authRoutes); // Rutas de login y registro
app.use('/api/Solicitudes', solicitudesRoutes); // Rutas de solicitudes
app.use('/api/files', fileRoutes); // Manejo de archivos
app.use('/api/users', userRoutes); // Rutas para crear/ver usuarios (nuevas)

// 3) Ruta de prueba
app.get('/', (req, res) => {
  res.send('Back-end server is running!');
});

// 4) Ruta temporal para crear empleado (a reemplazar con control de roles luego)
app.post('/employees', async (req, res) => {
  const { nombre, correo } = req.body;
  try {
    const result = await pool.query(
      'INSERT INTO lae_user (nombre, user_email) VALUES ($1, $2) RETURNING *',
      [nombre, correo]
    );
    res.json({ success: true, empleado: result.rows[0] });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, error: err.message });
  }
});

// 5) Arrancar servidor
app.listen(port, () => {
  console.log(`Back-end server running at http://localhost:${port}`);
});
