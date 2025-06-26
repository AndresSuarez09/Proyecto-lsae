require('dotenv').config();
const express = require('express');
const cors = require('cors');
const pool = require('./db');
const authRoutes = require('./routes/authRoutes');
const solicitudesRoutes = require('./routes/solicitudesRoutes');
const fileRoutes = require('./routes/fileRoutes');
const userRoutes = require('./routes/userRoutes');
const certificadoRoutes = require('./routes/certificadoRoutes');
const app = express();
const port = process.env.PORT || 3001;
const path = require('path');

// 1) Middlewares
app.use(cors({
  origin: ['https://lubrisolae.web.app', 'http://localhost:5173'], // Frontend producción y desarrollo
  methods: ['GET', 'POST', 'PUT', 'DELETE'], // Métodos permitidos
  credentials: true
}));
app.use(express.json()); // Para entender JSON en los cuerpos de petición

// 2) Registrar rutas
app.use('/api/auth', authRoutes);
app.use('/api/Solicitudes', solicitudesRoutes);
app.use('/api/files', fileRoutes);
app.use('/api/users', userRoutes);
app.use('/api/certificados', certificadoRoutes);
// 3) Rutas estáticas
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.static(path.join(__dirname, '../front/public')));
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));
app.use('/test', express.static(path.join(__dirname, 'web-test')));

// 4) Ruta de prueba
app.get('/', (req, res) => {
  res.send('Back-end server is running!');
});

// 5) Ruta temporal para crear empleado
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

// 6) Arrancar servidor
app.listen(port, () => {
  console.log(`Back-end server running at http://localhost:${port}`);
});
