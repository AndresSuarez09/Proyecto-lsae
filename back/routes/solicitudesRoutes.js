// back/routes/solicitudesRoutes.js
const express = require('express');
const router = express.Router();
const pool = require('../db');

// POST /api/solicitudes
// Crea una nueva solicitud
router.post('/', async (req, res) => {
  const { empleado_id, tipo_solicitud, descripcion } = req.body;
  try {
    const result = await pool.query(
      `INSERT INTO solicitudes 
        (empleado_id, tipo_solicitud, descripcion, fecha_solicitud)
       VALUES
        ($1, $2, $3, NOW())
       RETURNING *`,
      [empleado_id, tipo_solicitud, descripcion]
    );
    res.json({ success: true, solicitud: result.rows[0] });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false, error: err.message });
  }
});

module.exports = router;
