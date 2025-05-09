const express = require('express');
const multer = require('multer');
const path = require('path');
const router = express.Router();

// Configuración de almacenamiento con multer
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads'); // Carpeta donde se guardan los archivos
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1e9);
    cb(null, uniqueSuffix + '-' + file.originalname);
  }
});

const upload = multer({ storage });

// Ruta para subir un archivo
router.post('/upload', upload.single('archivo'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ success: false, message: 'No se subió ningún archivo' });
  }

  res.json({
    success: true,
    message: 'Archivo subido correctamente',
    filename: req.file.filename,
    url: `/uploads/${req.file.filename}`
  });
});

module.exports = router;
