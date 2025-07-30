require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const pool = require('./db');

const authRoutes = require('./routes/authRoutes');
const solicitudesRoutes = require('./routes/solicitudesRoutes');
const fileRoutes = require('./routes/fileRoutes');
const userRoutes = require('./routes/userRoutes');
const certificadoRoutes = require('./routes/certificadoRoutes');

const app = express();
const port = process.env.PORT || 3001;

// Middleware base
app.use(cors({
  origin: ['https://lubrisolae.web.app', 'http://localhost:5173'],
  credentials: true
}));
app.use(express.json());

// Rutas
app.use('/api/auth', authRoutes);
app.use('/api/Solicitudes', solicitudesRoutes);
app.use('/api/files', fileRoutes);
app.use('/api/users', userRoutes);
app.use('/api/certificados', certificadoRoutes);

// Archivos estáticos
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.static(path.join(__dirname, '../front/public')));
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));
app.use('/test', express.static(path.join(__dirname, 'web-test')));

// Ruta base
app.get('/', (req, res) => {
  res.send('✅ Back-end server is running!');
});

// Arranque final
app.listen(port, () => {
  console.log(`🚀 Servidor corriendo en http://localhost:${port}`);
});
