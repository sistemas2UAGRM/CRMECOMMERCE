# backend/main/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta
import dj_database_url

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-secret-key')
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() in ('1', 'true', 'yes')

ALLOWED_HOSTS = ['.localhost', '127.0.0.1', '10.0.2.2','localhost','*']

# Apps que viven en el esquema 'public' (Comunes a todos)
SHARED_APPS = (
    'django_tenants', 
    'apps.tenants',    

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_yasg',
    'corsheaders',
    'django_filters',
    'cloudinary',
    'cloudinary_storage',
    'django_countries',
    'phonenumber_field',
    'django_celery_results',

    'apps.users', 
    'apps.core',  
)

# Apps que viven en cada esquema de inquilino (Datos Privados)
TENANT_APPS = (
    # Django requiere estas apps también en los esquemas de inquilinos
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.messages',
    'django.contrib.admin', # Opcional, si quieres que cada tenant tenga su /admin

    # --- TUS APPS DE NEGOCIO (Aquí están los datos aislados) ---
    'apps.users',
    
    # E-commerce
    'apps.ecommerce.productos',
    'apps.ecommerce.pedidos',
    'apps.ecommerce.carritos',
    'apps.ecommerce.pagos',

    # CRM
    'apps.crm.crm_preventa',
    'apps.crm.calendario',
    'apps.crm.clientes',
    'apps.crm.soporte',
)

# Django Tenants combina ambas listas para que Django arranque
INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]

# Configuración del modelo de Inquilino
TENANT_MODEL = "tenants.Client" 
TENANT_DOMAIN_MODEL = "tenants.Domain"

AUTH_USER_MODEL = 'users.User'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # --- CAMBIO 2: MIDDLEWARE DE TENANTS ---
    'django_tenants.middleware.main.TenantMainMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'main.wsgi.application'

# --- VARIABLES DE ENTORNO ---
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
SITE_URL = os.getenv('SITE_URL', 'http://localhost:8000')
MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY')
MAILGUN_DOMAIN = os.getenv('MAILGUN_DOMAIN')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@tudominio.com')

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL')
    )
}

DATABASES['default']['ENGINE'] = 'django_tenants.postgresql_backend'

DATABASE_ROUTERS = (
    'django_tenants.routers.TenantSyncRouter',
)

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = os.getenv('TIME_ZONE', 'America/La_Paz')
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
MEDIA_URL = '/media/'  
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Mantemos del anterior backend
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

"""CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite
    "http://localhost:3000",  # React
    "http://localhost:8080",  # Vue
    "http://localhost:4200",  # Angular
    "http://localhost:4000",

    # En producción aquí irían tus dominios reales
    # "https://pepita.mitienda.com",
]"""

# Comenta o elimina CORS_ALLOWED_ORIGINS estático y usa esto:
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^http://.+\.localhost:5173$",   # Permite cualquier subdominio en puerto 5173
    r"^http://localhost:5173$",       # Permite localhost directo
    r"^http://.+\.localhost:3000$",   # Permite cualquier subdominio en puerto 3000
    r"^http://localhost:3000$",       # Permite localhost directo
    r"^http://.+\.localhost:8080$",   # Permite cualquier subdominio en puerto 8080
    r"^http://localhost:8080$",       # Permite localhost directo
    r"^http://.+\.localhost:4200$",   # Permite cualquier subdominio en puerto 4200
    r"^http://localhost:4200$",       # Permite localhost directo
    r"^http://.+\.localhost:4000$",   # Permite cualquier subdominio en puerto 4000
    r"^http://localhost:4000$",       # Permite localhost directo
    r"^http://.+\.10\.0\.2\.2:8000$",           # Emulador Android (alternativa)
    r"^http://.+\.192\.168\.\d+\.\d+:8000$",    # Dispositivo real
]

CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOW_CREDENTIALS = True

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'JWT Authorization header using the Bearer scheme.'
        }
    },
    'USE_SESSION_AUTH': False,
}

REDOC_SETTINGS = {'LAZY_RENDERING': False}

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = 'django-db' 
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True