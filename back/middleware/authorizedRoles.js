// back/middleware/authorizeRoles.js

module.exports = function authorizeUserCreation(req, res, next) {
  const currentUserRole = req.user?.role;       // Rol del usuario logueado (del token)
  const newUserRole = req.body.role;            // Rol del usuario a crear

  if (!currentUserRole || !newUserRole) {
    return res.status(400).json({ message: 'Rol no especificado correctamente' });
  }

  // Tabla de permisos según jerarquía
  const permisos = {
    1: [1, 2, 3], // Gerente puede crear Admin y Empleado
    2: [2, 3], // Admin puede crear Admin y Empleado
    3: [3],    // Empleado solo puede crear Empleado
  };

  if (!permisos[currentUserRole]?.includes(newUserRole)) {
    return res.status(403).json({ message: 'Acceso denegado: rol no autorizado' });
  }

  next();
};
