"""
wanderly/settings_production.py
================================
Production-ready settings for Wanderly.

USAGE:
    export DJANGO_SETTINGS_MODULE=wanderly.settings_production

Required environment variables:
    SECRET_KEY, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, ALLOWED_HOSTS
    WEATHER_API_KEY, AMADEUS_API_KEY, AMADEUS_API_SECRET

Install python-decouple for env-var management:
    pip install python-decouple
"""

import os
from pathlib import Path
from decouple import config, Csv  # pip install python-decouple

BASE_DIR = Path(__file__).resolve().parent.parent

# ─────────────────────────────────────────────────────────────
# 1. CORE SECURITY
# ─────────────────────────────────────────────────────────────

# SECRET_KEY is read from an environment variable — never hard-coded.
SECRET_KEY = config('SECRET_KEY')

# DEBUG must be False in production. Exposing tracebacks to users is a
# critical information-disclosure vulnerability.
DEBUG = False

# Explicit whitelist: only your domain(s) — never '*'.
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())
# Example .env entry:  ALLOWED_HOSTS=wanderly.com,www.wanderly.com

# ─────────────────────────────────────────────────────────────
# 2. HTTPS / COOKIE / HSTS SETTINGS
# ─────────────────────────────────────────────────────────────

# Force every HTTP request to redirect to HTTPS.
SECURE_SSL_REDIRECT = True

# Mark the session cookie as HTTPS-only.
# This prevents the cookie from being sent over a plain HTTP connection.
SESSION_COOKIE_SECURE = True

# Mark the CSRF cookie as HTTPS-only for the same reason.
CSRF_COOKIE_SECURE = True

# Prevent JavaScript from accessing the session cookie (XSS mitigation).
SESSION_COOKIE_HTTPONLY = True

# HttpOnly for CSRF cookie as well.
CSRF_COOKIE_HTTPONLY = True

# Auto-logout after 30 minutes of inactivity (1800 seconds).
# Increase for lower-risk users; 30 min is appropriate for partners/admins.
SESSION_COOKIE_AGE = 1800

# Reset the session timer on every request so active users stay logged in.
SESSION_SAVE_EVERY_REQUEST = True

# Expire the session when the browser is closed (no persistent cookie).
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# HTTP Strict Transport Security: tell browsers to always use HTTPS.
# 1 year in seconds. Only enable once HTTPS is fully working.
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Prevent the browser from guessing content types (stops MIME-sniffing attacks).
SECURE_CONTENT_TYPE_NOSNIFF = True

# Activate the browser's built-in XSS filter.
SECURE_BROWSER_XSS_FILTER = True

# Deny embedding your site in an iframe (clickjacking protection).
X_FRAME_OPTIONS = 'DENY'

# ─────────────────────────────────────────────────────────────
# 3. INSTALLED APPS
# ─────────────────────────────────────────────────────────────

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'accounts',
    'partners',
    'locations',
    'posts',
    'booking',
    'flights',
    'chat',
    'notifications',
    'reviews',
    'core',
]

# ─────────────────────────────────────────────────────────────
# 4. MIDDLEWARE (order matters)
# ─────────────────────────────────────────────────────────────

MIDDLEWARE = [
    # SecurityMiddleware should be first so it handles redirects early.
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'wanderly.urls'

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

WSGI_APPLICATION = 'wanderly.wsgi.application'
ASGI_APPLICATION = 'wanderly.asgi.application'

# Use Redis for Channel Layers in production (not in-memory).
# pip install channels-redis
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [config('REDIS_URL', default='redis://127.0.0.1:6379')],
        },
    },
}

# ─────────────────────────────────────────────────────────────
# 5. DATABASE (PostgreSQL)
# ─────────────────────────────────────────────────────────────

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        # SSL for encrypted transport to the database server.
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

# ─────────────────────────────────────────────────────────────
# 6. AUTH & PASSWORD POLICY
# ─────────────────────────────────────────────────────────────

AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

AUTH_PASSWORD_VALIDATORS = [
    # Rejects passwords that are too similar to the user's own attributes.
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    # Requires a minimum length. 12 characters is the current industry standard.
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 12},
    },
    # Rejects passwords that appear in a list of 20 000+ common passwords.
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    # Rejects passwords that are entirely numeric.
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ─────────────────────────────────────────────────────────────
# 7. STATIC & MEDIA FILES
# ─────────────────────────────────────────────────────────────

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Legal / verification documents are stored outside MEDIA_ROOT and are
# served through Django with access control (see partners/views.py).
PRIVATE_MEDIA_ROOT = config('PRIVATE_MEDIA_ROOT', default='/srv/wanderly/private_media')

# ─────────────────────────────────────────────────────────────
# 8. LOGGING (structured, to file + console)
# ─────────────────────────────────────────────────────────────

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': config('LOG_FILE', default='/var/log/wanderly/django.log'),
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'WARNING',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# ─────────────────────────────────────────────────────────────
# 9. EXTERNAL API KEYS (from environment)
# ─────────────────────────────────────────────────────────────

WEATHER_API_KEY = config('WEATHER_API_KEY')
WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/weather'

AMADEUS_API_KEY = config('AMADEUS_API_KEY')
AMADEUS_API_SECRET = config('AMADEUS_API_SECRET')

# Used by stripe webhook validator (see booking/views.py)
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='')
STRIPE_WEBHOOK_SECRET = config('STRIPE_WEBHOOK_SECRET', default='')

# ─────────────────────────────────────────────────────────────
# 10. APP-SPECIFIC CONSTANTS
# ─────────────────────────────────────────────────────────────

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CHAT_MESSAGE_EXPIRY_DAYS = 180
POST_LIMIT_PER_PARTNER = 5
MAX_PLACES_PER_CITY = 20
MAX_IMAGES_PER_POST = 5
