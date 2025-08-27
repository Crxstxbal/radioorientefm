require('dotenv').config();
const express = require('express');
const cors = require('cors');
const bcrypt = require('bcrypt');
const { Pool } = require('pg');
const jwt = require('jsonwebtoken');
const nodemailer = require('nodemailer');

const app = express();
app.use(cors());
app.use(express.json());

// Conexión a la BD
const db = new Pool({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_DATABASE,
  port: process.env.DB_PORT,
});

// Importar rutas de contacto
const contactoRoutes = require('./routes/contacto')(db);
app.use('/api', contactoRoutes);

// Obtener usuarios (sin contraseñas)
app.get('/api/usuarios', async (req, res) => {
  try {
    const result = await db.query('SELECT id, nombre, usuario, correo FROM usuarios');
    res.json(result.rows);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Error en el servidor' });
  }
});

// Registrar usuario (cifra la contraseña)
app.post('/api/usuarios', async (req, res) => {
  try {
    const { nombre, usuario, correo, password } = req.body;

    if (!nombre || !usuario || !correo || !password) {
      return res.status(400).json({ error: 'Faltan datos requeridos' });
    }

    const check = await db.query(
      'SELECT id FROM usuarios WHERE usuario = $1 OR correo = $2',
      [usuario, correo]
    );
    if (check.rows.length > 0) {
      return res.status(409).json({ error: 'Usuario o correo ya registrado' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);

    const insert = await db.query(
      `INSERT INTO usuarios (nombre, usuario, correo, password) 
       VALUES ($1, $2, $3, $4) RETURNING id, nombre, usuario, correo`,
      [nombre, usuario, correo, hashedPassword]
    );

    res.status(201).json(insert.rows[0]);
  } catch (err) {
    console.error('Error al registrar usuario:', err);
    res.status(500).json({ error: 'Error en el servidor' });
  }
});

app.post('/api/login', async (req, res) => {
  try {
    const { identificador, password } = req.body; // puede ser usuario o correo

    if (!identificador || !password) {
      return res.status(400).json({ error: 'Faltan datos requeridos' });
    }

    const userRes = await db.query(
      'SELECT id, nombre, usuario, correo, password FROM usuarios WHERE usuario = $1 OR correo = $1',
      [identificador]
    );

    if (userRes.rows.length === 0) {
      return res.status(401).json({ error: 'Usuario o contraseña incorrectos' });
    }

    const user = userRes.rows[0];
    const validPass = await bcrypt.compare(password, user.password);

    if (!validPass) {
      return res.status(401).json({ error: 'Usuario o contraseña incorrectos' });
    }

    const { password: _, ...userSafe } = user;
    res.json(userSafe);

  } catch (err) {
    console.error('Error en login:', err);
    res.status(500).json({ error: 'Error en el servidor' });
  }
});

// Ruta para resetear contraseña
app.post('/api/resetear', async (req, res) => {
  try {
    const { token, nuevaPassword } = req.body;

    if (!token || !nuevaPassword) {
      return res.status(400).json({ error: 'Faltan datos requeridos' });
    }

    let payload;
    try {
      payload = jwt.verify(token, process.env.JWT_SECRET);
    } catch (err) {
      return res.status(401).json({ error: 'Token inválido o expirado' });
    }

    const usuarioId = payload.id;

    const hashedPassword = await bcrypt.hash(nuevaPassword, 10);

    await db.query('UPDATE usuarios SET password = $1 WHERE id = $2', [
      hashedPassword,
      usuarioId,
    ]);

    res.json({ mensaje: 'Contraseña actualizada correctamente' });
  } catch (error) {
    console.error('Error en resetear contraseña:', error);
    res.status(500).json({ error: 'Error en el servidor' });
  }
});

// Recuperar contraseña: envía correo con link
app.post('/api/recuperar', async (req, res) => {
  const { correo } = req.body;

  try {
    const result = await db.query('SELECT * FROM usuarios WHERE correo = $1', [correo]);

    if (result.rows.length === 0) {
      return res.status(404).json({ mensaje: "Correo no registrado" });
    }

    const usuario = result.rows[0];

    const token = jwt.sign({ id: usuario.id }, process.env.JWT_SECRET, { expiresIn: "15m" });

    const urlRecuperacion = `${process.env.FRONTEND_URL}/recuperar/${token}`;

    const transporter = nodemailer.createTransport({
      service: "gmail",
      auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASS,
      },
    });

    await transporter.sendMail({
      from: `"Radio Oriente" <${process.env.EMAIL_USER}>`,
      to: correo,
      subject: "Recupera tu contraseña",
      html: `
        <p>Hola ${usuario.nombre},</p>
        <p>Haz clic en el siguiente enlace para cambiar tu contraseña (válido por 15 minutos):</p>
        <a href="${urlRecuperacion}">${urlRecuperacion}</a>
      `,
    });

    res.json({ mensaje: "Correo de recuperación enviado" });
  } catch (err) {
    console.error("Error al enviar correo de recuperación:", err);
    res.status(500).json({ mensaje: "Error interno del servidor" });
  }
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`Backend corriendo en http://localhost:${PORT}`);
});
