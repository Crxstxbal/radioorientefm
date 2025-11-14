# Guía de Configuración Rápida - Radio Oriente FM

## Pasos Iniciales

### 1. Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd RADIOORIENTECORREGIDO
```

### 2. Configurar Backend

```bash
cd backend

# Copiar archivo de configuración
cp .env.example .env

# Generar SECRET_KEY segura
python generate_secret_key.py

# Copiar la SECRET_KEY generada al archivo .env
# Editar .env y pegar la clave en la línea SECRET_KEY=...

# Crear entorno virtual (opcional pero recomendado)
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar servidor de desarrollo
python manage.py runserver
```

### 3. Configurar Frontend

```bash
cd frontend

# Copiar archivo de configuración
cp .env.example .env

# Instalar dependencias
npm install

# Ejecutar servidor de desarrollo
npm start
```

### 4. Acceder a la Aplicación

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000/api/
- **Dashboard Admin:** http://localhost:8000/dashboard/

## Configuración de Base de Datos

### Desarrollo (SQLite)

En `backend/.env`:
```env
USE_SQLITE=True
```

### Producción (PostgreSQL/Supabase)

En `backend/.env`:
```env
USE_SQLITE=False
DATABASE_URL=postgresql://user:password@host:port/database
```

Obtén la `DATABASE_URL` desde:
**Supabase > Project Settings > Database > Connection string > URI**

## Configuración de Email

Para recuperación de contraseñas, configura en `backend/.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
DEFAULT_FROM_EMAIL=tu-email@gmail.com
```

Para Gmail, crea una App Password en:
https://myaccount.google.com/apppasswords

## Variables de Entorno Importantes

### Backend (`backend/.env`)

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `SECRET_KEY` | Clave secreta de Django | Generar con `generate_secret_key.py` |
| `DEBUG` | Modo debug | `True` (desarrollo) |
| `USE_SQLITE` | Usar SQLite en vez de PostgreSQL | `True` (desarrollo) |
| `DATABASE_URL` | URL de PostgreSQL | - |
| `CORS_ALLOW_ALL_ORIGINS` | Permitir todos los orígenes CORS | `True` (desarrollo) |
| `ALLOWED_ORIGINS` | Orígenes CORS permitidos | `http://localhost:3000` |
| `ALLOWED_HOSTS` | Hosts permitidos | `localhost,127.0.0.1` |

### Frontend (`frontend/.env`)

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `VITE_API_URL` | URL del backend | `http://localhost:8000` |
| `VITE_DASHBOARD_URL` | URL del dashboard | `http://localhost:8000/dashboard/` |

## Solución de Problemas

### Error: ModuleNotFoundError

```bash
# Asegúrate de tener el entorno virtual activado
pip install -r requirements.txt
```

### Error: CORS

Verifica que `ALLOWED_ORIGINS` en `backend/.env` incluya la URL del frontend:
```env
ALLOWED_ORIGINS=http://localhost:3000
```

### Error: Database

Si usas PostgreSQL, verifica que:
1. `USE_SQLITE=False` en `.env`
2. `DATABASE_URL` esté correctamente configurada
3. Las migraciones estén ejecutadas: `python manage.py migrate`

## Seguridad

**IMPORTANTE:** Lee [SECURITY.md](SECURITY.md) antes de desplegar a producción.

## Soporte

Proyecto académico desarrollado por:
- Leonardo Montenegro
- Cristóbal Castro
- Joaquín Molina

Curso: APT122