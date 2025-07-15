const express = require('express');
const router = express.Router();
const { createUser, getOwnProfile } = require('../controllers/userController');
const authMiddleware = require('../middleware/authMiddleware');
const authorizedRoles = require('../middleware/authorizedRoles'); // este ya usa la lógica de jerarquía

console.log('Cargando rutas de usuario...');

// Ruta protegida para crear usuarios con verificación jerárquica
router.post('/create', authMiddleware, authorizedRoles, createUser);

// Ruta para que cualquier usuario vea su propio perfil
router.get('/me', authMiddleware, getOwnProfile);

// Nueva ruta para editar perfil privado
router.put('/me/update', authMiddleware, updateOwnProfile);

module.exports = router;
