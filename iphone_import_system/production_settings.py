# Production settings for deployment platforms
import os
from .settings import *

# Override settings for production
DEBUG = False

# Security settings for production
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True, cast=bool)
SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=True, cast=bool)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Static files configuration for production
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Add whitenoise for static file serving
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Database configuration for production
# Prefer PostgreSQL for production, fallback to SQLite
if config('DATABASE_URL', default=''):
    import dj_database_url
    DATABASES['default'] = dj_database_url.parse(config('DATABASE_URL'))
elif config('SUPABASE_DB_PASSWORD', default=''):
    # Use Supabase PostgreSQL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'postgres',
            'USER': 'postgres.whkxlrzscxuctkwtdknj',
            'PASSWORD': config('SUPABASE_DB_PASSWORD'),
            'HOST': 'aws-0-us-east-1.pooler.supabase.com',
            'PORT': '6543',
            'OPTIONS': {
                'sslmode': 'require',
            },
        }
    }
else:
    # Fallback to SQLite for platforms that don't support PostgreSQL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': config('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
    },
}
