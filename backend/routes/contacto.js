const express = require('express');

module.exports = (db) => {
  const router = express.Router();

  router.post('/contacto', async (req, res) => {
    const { nombre, correo, telefono, asunto, mensaje } = req.body;

    if (!nombre || !correo || !asunto || !mensaje) {
      return res.status(400).json({ error: 'Faltan campos obligatorios' });
    }

    try {
      await db.query(
        `INSERT INTO formulario_contacto (nombre, correo, telefono, asunto, mensaje) VALUES ($1, $2, $3, $4, $5)`,
        [nombre, correo, telefono, asunto, mensaje]
      );

      res.status(200).json({ mensaje: 'Formulario enviado con éxito' });
    } catch (error) {
      console.error('Error al guardar formulario:', error);
      res.status(500).json({ error: 'Error al guardar formulario' });
    }
  });

  return router;
};
