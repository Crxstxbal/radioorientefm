import os
from pathlib import Path
from decouple import config

import dj_database_url
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# Configuración de hosts permitidos
ALLOWED_HOSTS_STR = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,0.0.0.0')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STR.split(',') if host.strip()]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    # 'channels',  # Comentado temporalmente
    
    # Apps normalizadas
    'apps.ubicacion',
    'apps.users',
    'apps.radio',
    'apps.articulos',  # Renombrado de apps.blog
    'apps.chat',
    'apps.contact',
    'apps.emergente',
    'apps.publicidad',
    'apps.notifications',
    'dashboard',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'radio_oriente.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'radio_oriente.wsgi.application'
# ASGI_APPLICATION = 'radio_oriente.asgi.application'  # Comentado temporalmente

# Database configuration
USE_SQLITE = config('USE_SQLITE', default=True, cast=bool)

if USE_SQLITE:
    # SQLite con estructura normalizada
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'radio_oriente_normalized.db',
        }
    }
else:
    # Configuración para PostgreSQL (Producción con Supabase)
    # Utiliza la variable de entorno DATABASE_URL que incluye el pooler de conexiones.
    DATABASES = {
        'default': dj_database_url.config(
            # Lee la URL de la base de datos desde la variable de entorno DATABASE_URL.
            default=config('DATABASE_URL'),
            # Mantiene las conexiones abiertas para reutilizarlas (importante para el pooler).
            conn_max_age=600,
            # Exige el uso de SSL para una conexión segura, requerido por Supabase.
            ssl_require=True
        )
    }

# Supabase configuration
SUPABASE_URL = config('SUPABASE_URL', default='')
SUPABASE_KEY = config('SUPABASE_ANON_KEY', default='')

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Caracas'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'apps.common.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 20,
}

# CORS settings
# En desarrollo, permitir todos los orígenes para facilitar el desarrollo
CORS_ALLOW_ALL_ORIGINS = True  # Solo para desarrollo

# Lista de orígenes permitidos (se puede configurar desde .env)
# En producción, descomenta las siguientes líneas y configura los orígenes permitidos
# ALLOWED_ORIGINS_STR = config('ALLOWED_ORIGINS', default='http://localhost:3000,http://127.0.0.1:3000')
# CORS_ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS_STR.split(',') if origin.strip()]

# Métodos HTTP permitidos
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Cabeceras permitidas
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ALLOW_CREDENTIALS = True

# CSRF trusted origins (para permitir peticiones desde el frontend en desarrollo)
CSRF_TRUSTED_ORIGINS_STR = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000'
)
CSRF_TRUSTED_ORIGINS = [o.strip() for o in CSRF_TRUSTED_ORIGINS_STR.split(',') if o.strip()]

# Cookies en desarrollo
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# Channels configuration (comentado temporalmente)
# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels_redis.core.RedisChannelLayer',
#         'CONFIG': {
#             "hosts": [('127.0.0.1', 6379)],
#         },
#     },
# }

# Custom user model
AUTH_USER_MODEL = 'users.User'

# Login URLs
LOGIN_URL = '/dashboard/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/dashboard/login/'

# Email Configuration
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@radiooriente.com')

# Frontend URL (para enlaces en emails)
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:3000')