const createUser = async (req, res) => {
  // 📋 Log de entrada para depuración
  console.log("🆕 Datos recibidos para nuevo usuario:", req.body);

  const {
    telefono_privado,
    correo_privado,
    cuenta_bancaria,
    contacto_emergencia,
    telefono_emergencia,
    nivel_estudio,
    anio_finalizacion,
    escuela,
    estado_civil,
    hijos_dependientes,
    nacionalidad,
    identificacion,
    pasaporte,
    genero,
    nacimiento_fecha,
    nacimiento_lugar
  } = req.body;

  try {
    const result = await pool.query(
      `INSERT INTO lae_user (
        telefono_privado,
        correo_privado,
        cuenta_bancaria,
        contacto_emergencia,
        telefono_emergencia,
        nivel_estudio,
        anio_finalizacion,
        escuela,
        estado_civil,
        hijos_dependientes,
        nacionalidad,
        identificacion,
        pasaporte,
        genero,
        nacimiento_fecha,
        nacimiento_lugar
      ) VALUES (
        $1, $2, $3, $4, $5,
        $6, $7, $8, $9, $10,
        $11, $12, $13, $14, $15, $16
      ) RETURNING id_user`,
      [
        telefono_privado || null,
        correo_privado || null,
        cuenta_bancaria || null,
        contacto_emergencia || null,
        telefono_emergencia || null,
        nivel_estudio || null,
        anio_finalizacion || null,
        escuela || null,
        estado_civil || null,
        parseInt(hijos_dependientes) || 0,
        nacionalidad || null,
        identificacion || null,
        pasaporte || null,
        genero || null,
        nacimiento_fecha || null,
        nacimiento_lugar || null
      ]
    );

    const newUserId = result.rows[0].id_user;
    console.log("✅ Usuario creado con ID:", newUserId);
    res.status(201).json({ message: 'Usuario creado exitosamente', id: newUserId });

  } catch (err) {
    console.error("❌ Error al crear usuario:", err.message);
    res.status(500).json({ message: 'Error interno al registrar usuario' });
  }
};
