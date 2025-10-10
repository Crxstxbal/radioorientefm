
-- =========================================
-- TABLAS DE DJANGO (sin modificaciones)
-- =========================================

CREATE TABLE auth_group (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE auth_permission (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_type_id INTEGER NOT NULL,
    codename VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    UNIQUE(content_type_id, codename),
    FOREIGN KEY(content_type_id) REFERENCES django_content_type(id)
);

CREATE TABLE auth_group_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    UNIQUE(group_id, permission_id),
    FOREIGN KEY(group_id) REFERENCES auth_group(id),
    FOREIGN KEY(permission_id) REFERENCES auth_permission(id)
);

CREATE TABLE django_content_type (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    UNIQUE(app_label, model)
);

CREATE TABLE django_migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied TIMESTAMP NOT NULL
);

CREATE TABLE django_session (
    session_key VARCHAR(40) PRIMARY KEY,
    session_data TEXT NOT NULL,
    expire_date TIMESTAMP NOT NULL
);

CREATE TABLE authtoken_token (
    key VARCHAR(40) PRIMARY KEY,
    created TIMESTAMP NOT NULL,
    user_id INTEGER NOT NULL,
    UNIQUE(user_id),
    FOREIGN KEY(user_id) REFERENCES usuario(id)
);

CREATE TABLE usuario_permission (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    UNIQUE(usuario_id, permission_id),
    FOREIGN KEY(usuario_id) REFERENCES usuario(id),
    FOREIGN KEY(permission_id) REFERENCES auth_permission(id)
);

CREATE TABLE usuario_group (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    UNIQUE(usuario_id, group_id),
    FOREIGN KEY(usuario_id) REFERENCES usuario(id),
    FOREIGN KEY(group_id) REFERENCES auth_group(id)
);

CREATE TABLE django_admin_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    object_id TEXT,
    object_repr VARCHAR(200) NOT NULL,
    action_flag INTEGER NOT NULL CHECK(action_flag >= 0),
    change_message TEXT NOT NULL,
    content_type_id INTEGER,
    user_id INTEGER NOT NULL,
    action_time TIMESTAMP NOT NULL,
    FOREIGN KEY(content_type_id) REFERENCES django_content_type(id),
    FOREIGN KEY(user_id) REFERENCES usuario(id)
);

-- =========================================
-- TABLAS MODIFICADAS SEGÚN INSTRUCCIONES
-- =========================================

CREATE TABLE rol (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT
);

CREATE TABLE usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    password VARCHAR(128) NOT NULL,
    is_superuser BOOLEAN NOT NULL DEFAULT 0,
    is_staff BOOLEAN NOT NULL DEFAULT 0,
    username VARCHAR(150) NOT NULL UNIQUE,
    email VARCHAR(254) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    rol_id INTEGER,
    FOREIGN KEY(rol_id) REFERENCES rol(id)
);

CREATE TABLE tipo_asunto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL
);

CREATE TABLE contacto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    asunto_id INTEGER NOT NULL,
    mensaje TEXT NOT NULL,
    fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_respuesta TIMESTAMP,
    FOREIGN KEY(usuario_id) REFERENCES usuario(id),
    FOREIGN KEY(asunto_id) REFERENCES tipo_asunto(id)
);

CREATE TABLE banda_emergente (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_banda VARCHAR(150) NOT NULL,
    documento_presentacion TEXT,
    ciudad VARCHAR(100),
    pais VARCHAR(100),
    email_contacto VARCHAR(254) NOT NULL,
    telefono_contacto VARCHAR(20),
    mensaje TEXT NOT NULL,
    genero_id INTEGER NOT NULL,
    usuario_id INTEGER,
    estado_id INTEGER NOT NULL,
    fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_revision TIMESTAMP,
    revisado_por_id INTEGER,
    FOREIGN KEY(genero_id) REFERENCES genero_musical(id),
    FOREIGN KEY(usuario_id) REFERENCES usuario(id),
    FOREIGN KEY(estado_id) REFERENCES estado(id),
    FOREIGN KEY(revisado_por_id) REFERENCES usuario(id)
);

CREATE TABLE integrante (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    banda_id INTEGER NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    FOREIGN KEY(banda_id) REFERENCES banda_emergente(id) ON DELETE CASCADE
);

CREATE TABLE banda_link (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    banda_id INTEGER NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    url VARCHAR(500) NOT NULL,
    FOREIGN KEY(banda_id) REFERENCES banda_emergente(id) ON DELETE CASCADE
);

CREATE TABLE categoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT
);

CREATE TABLE articulo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo VARCHAR(200) NOT NULL,
    slug VARCHAR(250) NOT NULL UNIQUE,
    contenido TEXT NOT NULL,
    resumen TEXT,
    imagen_url VARCHAR(500),
    autor_id INTEGER NOT NULL,
    categoria_id INTEGER NOT NULL,
    publicado BOOLEAN NOT NULL DEFAULT 0,
    destacado BOOLEAN NOT NULL DEFAULT 0,
    fecha_publicacion TIMESTAMP,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(autor_id) REFERENCES usuario(id),
    FOREIGN KEY(categoria_id) REFERENCES categoria(id)
);

CREATE TABLE conductor (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(150) NOT NULL,
    apellido VARCHAR(150) NOT NULL,
    apodo VARCHAR(150)
);

CREATE TABLE programa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    imagen_url VARCHAR(500),
    activo BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE horario_programa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    programa_id INTEGER NOT NULL,
    dia_semana INTEGER NOT NULL CHECK(dia_semana BETWEEN 0 AND 6),
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT 1,
    FOREIGN KEY(programa_id) REFERENCES programa(id)
);

CREATE TABLE programa_conductor (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    programa_id INTEGER NOT NULL,
    conductor_id INTEGER NOT NULL,
    FOREIGN KEY(programa_id) REFERENCES programa(id),
    FOREIGN KEY(conductor_id) REFERENCES conductor(id)
);

CREATE TABLE estacion_radio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    stream_url VARCHAR(500),
    telefono VARCHAR(20),
    email VARCHAR(254),
    direccion TEXT,
    listeners_count INTEGER NOT NULL DEFAULT 0
);

-- =========================================
-- PUBLICIDAD
-- =========================================

CREATE TABLE publicidad (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_cliente VARCHAR(100) NOT NULL,
    descripcion TEXT,
    tipo VARCHAR(10) NOT NULL CHECK(tipo IN ('WEB','RADIAL')),
    fecha_inicio DATE,
    fecha_fin DATE,
    activo BOOLEAN NOT NULL DEFAULT 1,
    costo_total DECIMAL,
    archivo_media TEXT,
    usuario_id INTEGER NOT NULL,
    FOREIGN KEY(usuario_id) REFERENCES usuario(id)
);

CREATE TABLE publicidad_web (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    publicidad_id INTEGER NOT NULL,
    ubicacion VARCHAR(50) NOT NULL CHECK(ubicacion IN ('banner_superior','lateral','footer')),
    formato VARCHAR(50),
    url_destino VARCHAR(250),
    impresiones INTEGER DEFAULT 0,
    clics INTEGER DEFAULT 0,
    costo_por_dia DECIMAL,
    FOREIGN KEY(publicidad_id) REFERENCES publicidad(id)
);

CREATE TABLE publicidad_radial (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    publicidad_id INTEGER NOT NULL,
    programa_id INTEGER NOT NULL,
    horario_id INTEGER NOT NULL,
    duracion_segundos INTEGER NOT NULL,
    valor_por_segundo DECIMAL,
    costo_total DECIMAL,
    FOREIGN KEY(publicidad_id) REFERENCES publicidad(id),
    FOREIGN KEY(programa_id) REFERENCES programa(id),
    FOREIGN KEY(horario_id) REFERENCES horario_programa(id)
);

-- =========================================
-- GENERO_MUSICAL Y ESTADO
-- =========================================

CREATE TABLE genero_musical (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT
);

CREATE TABLE estado (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    tipo_entidad INTEGER NOT NULL
);
