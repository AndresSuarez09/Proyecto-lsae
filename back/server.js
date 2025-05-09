require('dotenv').config();
const express = require('express');
const cors = require('cors');
const pool = require('./db');      // Tu conexión PostgreSQL
const authRoutes = require('./routes/authRoutes');  //añadido
const solicitudesRoutes = require('./routes/solicitudesRoutes'); //añadido
const app = express();
const port = process.env.PORT || 3001;
const fileRoutes = require('./routes/fileRoutes'); //carga y descarga archivos
const path = require('path'); //añadido


// 1) Middlewares
app.use(cors());                   // Permite peticiones desde cualquier origen
app.use(express.json());           // Para entender JSON en los cuerpos de petición
app.use(express.static('public')); // Sirve forms.html desde back/public
app.use('/uploads', express.static(path.join(__dirname, 'uploads'))); //añadido para servir archivos
app.use('/api/files', fileRoutes); //añadido para manejar subida de archivos


//1.1) Usar rutas de autenticación
app.use('/api/auth', authRoutes);  //añadido
//Ruta para solicitudes
app.use('/api/Solicitudes', solicitudesRoutes); //añadido
// 2) Ruta de prueba
app.get('/', (req, res) => {
  res.send('Back-end server is running!');
});

// 3) Endpoint para crear un empleado
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

// 4) Arrancar servidor
app.listen(port, () => {
  console.log(`Back-end server running at http://localhost:${port}`);
});
