const express = require('express');
const router = express.Router();

const {
  createUser,
  getOwnProfile,
  updateOwnProfile,
  deleteOwnProfile
} = require('../controllers/userController');

const authMiddleware = require('../middleware/authMiddleware');
const authorizedRoles = require('../middleware/authorizedRoles');

console.log('📦 Cargando rutas de usuario...');

router.post('/create', authMiddleware, authorizedRoles, createUser);
router.get('/me', authMiddleware, getOwnProfile);
router.put('/me/update', authMiddleware, updateOwnProfile);
router.delete('/me/delete', authMiddleware, deleteOwnProfile);

module.exports = router;
