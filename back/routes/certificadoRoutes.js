const express = require('express');
const PDFDocument = require('pdfkit');
const pool = require('../db');

const router = express.Router();

router.get('/:id', async (req, res) => {
  const userId = req.params.id;

  try {
    const result = await pool.query(
      'SELECT user_name FROM lae_user WHERE id_user = $1',
      [userId]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Usuario no encontrado' });
    }

    const nombre = result.rows[0].user_name;
    const doc = new PDFDocument();

    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', `attachment; filename=certificado_${userId}.pdf`);

    doc.pipe(res);

    doc.fontSize(14).text('Consecutivo: 25-002', { align: 'right' });
    doc.moveDown(2);
    doc.fontSize(16).text('A QUIEN PUEDA INTERESAR', { align: 'center' });
    doc.moveDown();

    doc.fontSize(12).text(`Por medio de la presente, certificamos que: ${nombre}, identificado con C.C. No.: XXXXXX, trabaja en nuestra organización, LUBRICANTES Y SOLUBLES DE COLOMBIA LTDA, LUBRISOL DE COLOMBIA LTDA. con NIT 800.004.430-4; bajo contrato a XXXXXXX, ocupando el cargo de XXXXXXXX. Su fecha de ingreso a la organización fue el DD/mm/aaaa y su asignación mensual promedio se discrimina de la siguiente manera:`);
    doc.moveDown();
    doc.text('Salario Básico                 $ .000');
    doc.text('Subsidio de transporte        $ .000');
    doc.text('Subsidio de alimentación      $ .000');
    doc.moveDown();
    doc.text('TOTAL                          $ .000');
    doc.moveDown();
    doc.text('Para un total de CERO MIL PESOS M/CTE.');
    doc.moveDown();
    doc.text('Se expide a solicitud del interesado a los 20 (VEINTE) días del mes de ENERO de 2025 (DOS MIL VEINTICINCO).');
    doc.moveDown(4);
    doc.text('Marco Rodríguez', { align: 'left' });
    doc.text('Ing. Jefe I&D');
    doc.text('Lubrisol de Colombia Ltda.');

    doc.end();
  } catch (err) {
    console.error(err.message);
    res.status(500).json({ message: 'Error al generar el certificado' });
  }
});

module.exports = router;
