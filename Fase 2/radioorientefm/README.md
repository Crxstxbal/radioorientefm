# Radio Oriente FM

Sistema web completo para la gestion de una estacion de radio comunitaria. Incluye reproductor en vivo, chat en tiempo real, gestion de programacion, articulos de noticias, publicidad y formularios de contacto para bandas emergentes.

---

## Tabla de Contenidos

1. [Descripcion General](#descripcion-general)
2. [Arquitectura del Proyecto](#arquitectura-del-proyecto)
3. [Tecnologias Utilizadas](#tecnologias-utilizadas)
4. [Requisitos Previos](#requisitos-previos)
5. [Instalacion](#instalacion)
6. [Configuracion](#configuracion)
7. [Ejecucion](#ejecucion)
8. [Estructura del Proyecto](#estructura-del-proyecto)
9. [Modulos del Sistema](#modulos-del-sistema)
10. [API Endpoints](#api-endpoints)
11. [Base de Datos](#base-de-datos)
12. [Despliegue](#despliegue)

---

## Descripcion General

Radio Oriente FM es una plataforma web que permite:

- Transmision de radio en vivo con reproductor integrado
- Chat en tiempo real con filtro de contenido ofensivo (ML)
- Gestion de programacion y horarios
- Publicacion de articulos y noticias
- Sistema de publicidad web y radial (mediante gestión en Google Calendar)
- Formulario de postulacion para bandas emergentes
- Panel de administracion (Dashboard)
- Autenticacion de usuarios con soporte para Google OAuth

---

## Arquitectura del Proyecto

El proyecto sigue una arquitectura cliente-servidor separada:

```
radioorientefm/
├── backend/          # API REST con Django
└── frontend/         # Aplicacion React (SPA)
```

- **Backend**: Django 5.2 + Django REST Framework + Channels (WebSockets)
- **Frontend**: React 18 + Vite + React Router
- **Base de Datos**: PostgreSQL (Supabase en produccion) / SQLite (desarrollo y utilizado inicialmente)
- **Comunicacion**: API REST + WebSockets para chat en tiempo real

---

## Tecnologias Utilizadas

### Backend

| Tecnologia | Version | Uso |
|------------|---------|-----|
| Python | 3.12+ | Lenguaje principal |
| Django | 5.2.7 | Framework web |
| Django REST Framework | 3.16.1 | API REST |
| Channels | 4.x | WebSockets (chat en tiempo real) |
| Daphne | 4.x | Servidor ASGI |
| PostgreSQL | - | Base de datos (produccion) |
| SQLite | - | Base de datos (desarrollo) |
| Detoxify | 0.5.2 | Filtro de contenido ofensivo (ML) |
| Pillow | 12.0 | Procesamiento de imagenes |
| WhiteNoise | 6.11 | Archivos estaticos |
| psycopg2-binary | 2.9.11 | Driver PostgreSQL |

### Frontend

| Tecnologia | Version | Uso |
|------------|---------|-----|
| React | 18.2 | Framework UI |
| Vite | 7.x | Build tool |
| React Router | 6.30 | Enrutamiento |
| Axios | 1.12 | Cliente HTTP |
| Framer Motion | 12.x | Animaciones |
| Lucide React | 0.294 | Iconos |
| HLS.js | 1.6 | Reproductor de streaming |
| React Hot Toast | 2.6 | Notificaciones |

### Infraestructura

| Servicio | Uso |
|----------|-----|
| Render | Hosting del backend |
| Cloudflare | CDN y DNS |
| Supabase | Base de datos PostgreSQL |

---

## Requisitos Previos

- Python 3.12 o superior
- Node.js 18 o superior
- npm 9 o superior
- Git
- Cuenta en Supabase (para produccion)

---

## Instalacion

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd radioorientefm
```

### 2. Backend

```bash
cd backend

#Crear entorno virtual
python -m venv venv

#Activar entorno virtual
#Windows:
venv\Scripts\activate
#Linux/Mac:
source venv/bin/activate

#Instalar dependencias
pip install -r requirements.txt
```

### 3. Frontend

```bash
cd frontend

#Instalar dependencias
npm install
```

---

## Configuracion

### Backend

1. Copiar el archivo de ejemplo de variables de entorno:

```bash
cd backend
copy .env.example .env
```

2. Editar el archivo `.env` con los valores correspondientes:

```env
# Django
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True

# Base de datos
USE_SQLITE=True                    # False para usar PostgreSQL
DATABASE_URL=postgresql://...      # URL de Supabase

# Email (para recuperacion de contrasena)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password

# URLs
FRONTEND_URL=http://localhost:3000
DASHBOARD_URL=http://localhost:8000/dashboard/
```

3. Generar una SECRET_KEY segura:

```bash
python generate_secret_key.py
```

4. Aplicar migraciones:

```bash
python manage.py migrate
```

5. Crear superusuario:

```bash
python manage.py createsuperuser
```

### Frontend

1. Crear archivo `.env` en la carpeta frontend:

```env
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=tu-client-id-de-google
```

---

## Ejecucion

### Desarrollo

**Backend** (con soporte WebSocket):

```bash
cd backend
python -m daphne -b 0.0.0.0 -p 8000 radio_oriente.asgi:application
```

O sin WebSocket:

```bash
cd backend
python manage.py runserver
```

**Frontend**:

```bash
cd frontend
npm run dev
```

### URLs de acceso

| Servicio | URL |
|----------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Dashboard Admin | http://localhost:8000/dashboard/ |
| Django Admin | http://localhost:8000/admin/ |
| API Info | http://localhost:8000/info/ |

---

## Estructura del Proyecto

```
radioorientefm/
├── backend/
│   ├── apps/                      # Aplicaciones Django
│   │   ├── articulos/             # Gestion de articulos/noticias
│   │   ├── chat/                  # Chat en tiempo real
│   │   ├── common/                # Utilidades compartidas
│   │   ├── contact/               # Formularios de contacto
│   │   ├── emergente/             # Bandas emergentes
│   │   ├── notifications/         # Sistema de notificaciones
│   │   ├── publicidad/            # Gestion de publicidad
│   │   ├── radio/                 # Estacion, programas, conductores
│   │   ├── ubicacion/             # Regiones y comunas
│   │   └── users/                 # Usuarios personalizados
│   ├── dashboard/                 # Panel de administracion
│   │   ├── templates/             # Templates HTML del dashboard
│   │   ├── views.py               # Vistas del dashboard
│   │   └── urls.py                # Rutas del dashboard
│   ├── radio_oriente/             # Configuracion principal Django
│   │   ├── settings.py            # Configuracion
│   │   ├── urls.py                # Rutas principales
│   │   ├── asgi.py                # Configuracion ASGI
│   │   └── wsgi.py                # Configuracion WSGI
│   ├── media/                     # Archivos subidos por usuarios
│   ├── static/                    # Archivos estaticos
│   ├── templates/                 # Templates globales
│   ├── manage.py                  # CLI de Django
│   └── requirements.txt           # Dependencias Python
│
├── frontend/
│   ├── src/
│   │   ├── components/            # Componentes reutilizables
│   │   │   ├── Navbar.js          # Barra de navegacion
│   │   │   ├── Footer.js          # Pie de pagina
│   │   │   ├── RadioPlayer.js     # Reproductor de radio
│   │   │   ├── LiveChat.js        # Chat en tiempo real
│   │   │   ├── Emergente.js       # Formulario bandas emergentes
│   │   │   └── ...
│   │   ├── pages/                 # Paginas de la aplicacion
│   │   │   ├── Home.js            # Pagina principal
│   │   │   ├── EnVivo.js          # Transmision en vivo
│   │   │   ├── Programacion.js    # Parrilla programatica
│   │   │   ├── Articulos.js       # Listado de noticias
│   │   │   ├── Contacto.js        # Formulario de contacto
│   │   │   ├── PublicidadPage.js  # Solicitud de publicidad
│   │   │   └── ...
│   │   ├── contexts/              # Contextos de React
│   │   ├── layouts/               # Layouts de pagina
│   │   ├── utils/                 # Utilidades
│   │   ├── App.js                 # Componente principal
│   │   └── index.js               # Punto de entrada
│   ├── public/                    # Archivos publicos
│   ├── package.json               # Dependencias Node.js
│   └── vite.config.js             # Configuracion de Vite
│
├── .gitignore                     # Archivos ignorados por Git
└── README.md                      # Este archivo
```

---

## Modulos del Sistema

### 1. Radio (`apps.radio`)

Gestion de la estacion de radio, programas y conductores.

**Modelos**:
- `EstacionRadio`: Datos de la estacion (nombre, stream URL, estado)
- `Programa`: Programas de radio
- `Conductor`: Locutores y conductores
- `HorarioPrograma`: Horarios de emision
- `GeneroMusical`: Generos musicales
- `ReproduccionRadio`: Registro de oyentes

### 2. Usuarios (`apps.users`)

Sistema de autenticacion personalizado.

**Modelos**:
- `User`: Usuario personalizado con email como identificador principal

**Caracteristicas**:
- Autenticacion por email
- Soporte para Google OAuth
- Recuperacion de contrasena por email

### 3. Articulos (`apps.articulos`)

Sistema de publicacion de noticias y articulos.

**Modelos**:
- `Articulo`: Articulos con soporte multimedia
- `Categoria`: Categorias de articulos

**Caracteristicas**:
- Imagenes de portada y thumbnail
- Videos embebidos
- Archivos adjuntos
- Contador de vistas

### 4. Chat (`apps.chat`)

Chat en tiempo real con filtro de contenido.

**Modelos**:
- `ChatMessage`: Mensajes del chat
- `ContentFilterConfig`: Configuracion del filtro
- `PalabraProhibida`: Lista de palabras bloqueadas
- `InfraccionUsuario`: Registro de infracciones

**Caracteristicas**:
- WebSockets para tiempo real
- Filtro de toxicidad con ML (Detoxify)
- Sistema de strikes y bloqueo de usuarios

### 5. Publicidad (`apps.publicidad`)

Gestion de publicidad web y radial.

**Modelos**:
- `PublicidadWeb`: Banners y anuncios web
- `PublicidadRadial`: Spots de radio
- `SolicitudPublicidadWeb`: Solicitudes de clientes
- `UbicacionPublicidadWeb`: Espacios publicitarios

### 6. Bandas Emergentes (`apps.emergente`)

Formulario de postulacion para artistas.

**Modelos**:
- `BandaEmergente`: Datos de la banda
- `BandaLink`: Redes sociales y plataformas
- `BandaIntegrante`: Miembros de la banda
- `Integrante`: Datos de integrantes

### 7. Contacto (`apps.contact`)

Formularios de contacto general.

**Modelos**:
- `MensajeContacto`: Mensajes recibidos
- `Estado`: Estados de solicitudes (pendiente, aprobado, rechazado)

### 8. Ubicacion (`apps.ubicacion`)

Datos geograficos de Chile.

**Modelos**:
- `Region`: Regiones de Chile
- `Comuna`: Comunas por region

### 9. Notificaciones (`apps.notifications`)

Sistema de notificaciones para usuarios.

### 10. Dashboard

Panel de administracion web para gestionar todo el contenido.

**Secciones**:
- Inicio (estadisticas generales)
- Programacion (programas y horarios)
- Articulos (noticias)
- Chat (moderacion)
- Publicidad (gestion de anuncios)
- Bandas Emergentes (revision de postulaciones)
- Usuarios (gestion de cuentas)

---

## API Endpoints

Base URL: `http://localhost:8000/api/`

| Endpoint | Descripcion |
|----------|-------------|
| `/api/auth/` | Autenticacion (login, registro, token) |
| `/api/radio/` | Estacion, programas, conductores |
| `/api/articulos/` | CRUD de articulos |
| `/api/chat/` | Mensajes del chat |
| `/api/contact/` | Formularios de contacto |
| `/api/emergentes/` | Bandas emergentes |
| `/api/ubicacion/` | Regiones y comunas |
| `/api/publicidad/` | Gestion de publicidad |
| `/api/notifications/` | Notificaciones |

### Autenticacion

La API usa Token Authentication. Incluir en headers:

```
Authorization: Token <tu-token>
```

---

## Base de Datos

### Desarrollo (SQLite)

Por defecto, el proyecto usa SQLite para desarrollo local. No requiere configuracion adicional.

### Produccion (PostgreSQL / Supabase)

1. Crear proyecto en Supabase
2. Obtener la URL de conexion desde: Project Settings > Database > Connection string > URI
3. Configurar en `.env`:

```env
USE_SQLITE=False
DATABASE_URL=postgresql://postgres.[PROJECT_ID]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

### Migraciones

```bash
#Crear migraciones despues de cambios en modelos
python manage.py makemigrations

#Aplicar migraciones
python manage.py migrate

#Ver estado de migraciones
python manage.py showmigrations
```

---

## Despliegue

### Backend en Render

1. Crear nuevo Web Service en Render
2. Conectar repositorio de GitHub
3. Configurar:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `daphne -b 0.0.0.0 -p $PORT radio_oriente.asgi:application`
4. Agregar variables de entorno desde `.env`

### Frontend en Cloudflare Pages

1. Crear nuevo proyecto en Cloudflare Pages
2. Conectar repositorio
3. Configurar:
   - Build command: `npm run build`
   - Build output directory: `dist`
4. Agregar variables de entorno

---

## Comandos Utiles

```bash
#Backend
python manage.py runserver              #Servidor de desarrollo
python manage.py createsuperuser        #Crear admin
python manage.py makemigrations         #Crear migraciones
python manage.py migrate                #Aplicar migraciones
python manage.py collectstatic          #Recolectar archivos estaticos
python manage.py shell                  #Shell de Django

#Frontend
npm run dev                             #Servidor de desarrollo
npm run build                           #Build de produccion
npm run preview                         #Preview del build
```

---

## Zona Horaria

El sistema esta configurado para la zona horaria `America/Caracas` (UTC-4). Para cambiarla, modificar en `backend/radio_oriente/settings.py`:

```python
TIME_ZONE = 'America/Santiago'  #Ejemplo para Chile
```

---

## Soporte

Para reportar problemas o solicitar funcionalidades, crear un issue en el repositorio.

---

## Licencia

Este proyecto es de uso privado para Radio Oriente FM y creado por:
Cristóbal Castro
Joaquín Molina
Leonardo Montenegro 
