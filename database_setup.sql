-- Radio Oriente FM - Database Setup Script (Adaptado a esquema existente)
-- Ejecutar en Supabase SQL Editor

-- 1. Crear tabla estacion_radio
CREATE TABLE IF NOT EXISTS estacion_radio (
  id SERIAL PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  descripcion TEXT,
  stream_url VARCHAR(500),
  telefono VARCHAR(20),
  correo VARCHAR(150), -- Usar 'correo' como en tu esquema
  direccion TEXT,
  listeners_count INTEGER DEFAULT 0,
  activa BOOLEAN DEFAULT true,
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Crear tabla noticias
CREATE TABLE IF NOT EXISTS noticias (
  id SERIAL PRIMARY KEY,
  titulo VARCHAR(200) NOT NULL,
  contenido TEXT NOT NULL,
  resumen TEXT,
  imagen_url VARCHAR(500),
  autor_id INTEGER REFERENCES usuarios(id),
  autor_nombre VARCHAR(100),
  categoria VARCHAR(50),
  destacada BOOLEAN DEFAULT false,
  publicada BOOLEAN DEFAULT true,
  fecha_publicacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Crear tabla programacion
CREATE TABLE IF NOT EXISTS programacion (
  id SERIAL PRIMARY KEY,
  nombre_programa VARCHAR(100) NOT NULL,
  descripcion TEXT,
  conductor VARCHAR(100),
  dia_semana INTEGER NOT NULL, -- 0=Domingo, 1=Lunes, etc.
  hora_inicio TIME NOT NULL,
  hora_fin TIME NOT NULL,
  activo BOOLEAN DEFAULT true,
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Crear tabla blog_articulos
CREATE TABLE IF NOT EXISTS blog_articulos (
  id SERIAL PRIMARY KEY,
  titulo VARCHAR(200) NOT NULL,
  contenido TEXT NOT NULL,
  resumen TEXT,
  imagen_url VARCHAR(500),
  autor_id INTEGER REFERENCES usuarios(id),
  autor_nombre VARCHAR(100),
  categoria VARCHAR(50),
  tags TEXT[],
  publicado BOOLEAN DEFAULT true,
  fecha_publicacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Crear tabla blog_comentarios
CREATE TABLE IF NOT EXISTS blog_comentarios (
  id SERIAL PRIMARY KEY,
  articulo_id INTEGER REFERENCES blog_articulos(id) ON DELETE CASCADE,
  autor_nombre VARCHAR(100) NOT NULL,
  autor_correo VARCHAR(150), -- Usar 'correo' como en tu esquema
  contenido TEXT NOT NULL,
  aprobado BOOLEAN DEFAULT false,
  fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Crear tabla suscripciones
CREATE TABLE IF NOT EXISTS suscripciones (
  id SERIAL PRIMARY KEY,
  correo VARCHAR(150) NOT NULL UNIQUE, -- Usar 'correo' como en tu esquema
  nombre VARCHAR(100),
  activa BOOLEAN DEFAULT true,
  fecha_suscripcion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  token_unsuscribe VARCHAR(100) UNIQUE
);

-- 7. Mejorar tabla usuarios existente (manteniendo tu estructura)
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS first_name VARCHAR(50);
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS last_name VARCHAR(50);
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS is_staff BOOLEAN DEFAULT false;

-- 8. Mejorar tabla mensajes existente (manteniendo tu estructura)
ALTER TABLE mensajes ADD COLUMN IF NOT EXISTS usuario_nombre VARCHAR(100);
ALTER TABLE mensajes ADD COLUMN IF NOT EXISTS tipo VARCHAR(20) DEFAULT 'user';
ALTER TABLE mensajes ADD COLUMN IF NOT EXISTS sala VARCHAR(50) DEFAULT 'general';

-- 9. Insertar datos de ejemplo
INSERT INTO estacion_radio (nombre, descripcion, stream_url, telefono, correo, direccion, listeners_count) 
VALUES (
  'Radio Oriente FM',
  'La mejor música, noticias y entretenimiento de la Zona oriente de Santiago',
  'https://your-stream-url-here.com/stream',
  '+1-809-XXX-XXXX',
  'info@radioorientefm.com',
  'Zona Oriental, Santiago, República Dominicana',
  1250
) ON CONFLICT DO NOTHING;

-- 10. Insertar programación de ejemplo
INSERT INTO programacion (nombre_programa, descripcion, conductor, dia_semana, hora_inicio, hora_fin) VALUES
('Buenos Días Oriente', 'Programa matutino con noticias y música', 'María González', 1, '06:00', '09:00'),
('Música del Mediodía', 'Los mejores éxitos musicales', 'Carlos Rodríguez', 1, '12:00', '14:00'),
('Tarde Deportiva', 'Noticias y análisis deportivo', 'Luis Martínez', 1, '16:00', '18:00'),
('Noche Musical', 'Música variada para la noche', 'Ana Pérez', 1, '20:00', '23:00')
ON CONFLICT DO NOTHING;

-- 11. Insertar noticias de ejemplo
INSERT INTO noticias (titulo, contenido, resumen, autor_nombre, categoria, destacada) VALUES
('Radio Oriente FM celebra 15 años al aire', 'Nuestra querida emisora cumple 15 años conectando a la comunidad oriental con la mejor programación...', 'Celebramos nuestro aniversario con eventos especiales', 'Equipo Editorial', 'Institucional', true),
('Nuevo programa deportivo en las tardes', 'A partir del próximo lunes, tendremos un nuevo espacio dedicado al deporte local y nacional...', 'Tarde Deportiva llega a Radio Oriente FM', 'Carlos Rodríguez', 'Programación', false),
('Festival de música local este fin de semana', 'La zona oriental se prepara para recibir el festival de música más importante del año...', 'Gran festival musical en la región', 'María González', 'Eventos', true)
ON CONFLICT DO NOTHING;

-- 12. Insertar artículos de blog de ejemplo
INSERT INTO blog_articulos (titulo, contenido, resumen, autor_nombre, categoria, tags) VALUES
('La importancia de la radio comunitaria', 'La radio comunitaria juega un papel fundamental en el desarrollo social...', 'Reflexión sobre el impacto social de la radio', 'Equipo Editorial', 'Opinión', ARRAY['radio', 'comunidad', 'sociedad']),
('Historia de la música dominicana', 'Un recorrido por los géneros musicales que han marcado nuestra identidad...', 'Explorando nuestras raíces musicales', 'Ana Pérez', 'Cultura', ARRAY['música', 'cultura', 'dominicana'])
ON CONFLICT DO NOTHING;

-- 13. Habilitar RLS (Row Level Security) para seguridad
ALTER TABLE noticias ENABLE ROW LEVEL SECURITY;
ALTER TABLE blog_articulos ENABLE ROW LEVEL SECURITY;
ALTER TABLE blog_comentarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE suscripciones ENABLE ROW LEVEL SECURITY;

-- 14. Crear políticas básicas de seguridad
CREATE POLICY "Noticias públicas" ON noticias FOR SELECT USING (publicada = true);
CREATE POLICY "Blog público" ON blog_articulos FOR SELECT USING (publicado = true);
CREATE POLICY "Comentarios públicos" ON blog_comentarios FOR SELECT USING (aprobado = true);

-- 15. Crear índices para mejor rendimiento
CREATE INDEX IF NOT EXISTS idx_noticias_fecha ON noticias(fecha_publicacion DESC);
CREATE INDEX IF NOT EXISTS idx_noticias_categoria ON noticias(categoria);
CREATE INDEX IF NOT EXISTS idx_blog_fecha ON blog_articulos(fecha_publicacion DESC);
CREATE INDEX IF NOT EXISTS idx_programacion_dia ON programacion(dia_semana);
CREATE INDEX IF NOT EXISTS idx_mensajes_fecha ON mensajes(fecha_envio DESC);
