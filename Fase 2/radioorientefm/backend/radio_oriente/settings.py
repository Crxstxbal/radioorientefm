import os
from pathlib import Path
from decouple import config

import dj_database_url
#build paths inside the project like this: base_dir / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent

#security warning: keep the secret key used in production secret
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')

#security warning: don't run with debug turned on in production
DEBUG = config('DEBUG', default=True, cast=bool)

#configuracion de hosts permitidos
ALLOWED_HOSTS_STR = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,0.0.0.0')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STR.split(',') if host.strip()]

#application definition
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
    'channels',

    #apps normalizadas
    'apps.ubicacion',
    'apps.users',
    'apps.radio',
    'apps.articulos',
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
    'whitenoise.middleware.WhiteNoiseMiddleware',
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
ASGI_APPLICATION = 'radio_oriente.asgi.application'

#database configuration
USE_SQLITE = config('USE_SQLITE', default=True, cast=bool)

if USE_SQLITE:
    #sqlite con estructura normalizada
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'radio_oriente_normalized.db',
        }
    }
else:
    #configuracion para postgresql (producción con supabase)
    #configuracion de base de datos
    DATABASES = {
        'default': dj_database_url.config(
            #url de base de datos
            default=config('DATABASE_URL'),
            #reutilizar conexiones
            conn_max_age=600,
            #conexion ssl requerida
            ssl_require=True
        )
    }

#supabase configuration
SUPABASE_URL = config('SUPABASE_URL', default='')
SUPABASE_KEY = config('SUPABASE_ANON_KEY', default='')

#password validation
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

#internationalization
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Caracas'
USE_I18N = True
USE_TZ = True

#static files (css, javascript, images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

#default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#django rest framework
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

#cors settings
#en desarrollo, permitir todos los orígenes para facilitar el desarrollo
CORS_ALLOW_ALL_ORIGINS = True  #solo para desarrollo

#lista de orígenes permitidos (se puede configurar desde .env)
#en producción, descomenta las siguientes líneas y configura los orígenes permitidos
#allowed_origins_str = config('allowed_origins', default='http://localhost:3000,http://127.0.0.1:3000')
#cors_allowed_origins = [origin.strip() for origin in allowed_origins_str.split(',') if origin.strip()]

#metodos http permitidos
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

#cabeceras permitidas
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

#csrf trusted origins (para permitir peticiones desde el frontend en desarrollo)
CSRF_TRUSTED_ORIGINS_STR = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000'
)
CSRF_TRUSTED_ORIGINS = [o.strip() for o in CSRF_TRUSTED_ORIGINS_STR.split(',') if o.strip()]

#cookies en desarrollo
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

#channels configuration (desarrollo: capa en memoria)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

#custom user model
AUTH_USER_MODEL = 'users.User'

#login urls
LOGIN_URL = '/dashboard/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/dashboard/login/'

#email configuration
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@radiooriente.com')

#frontend url (para enlaces en emails)
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:3000')