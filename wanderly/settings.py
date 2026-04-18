"""
Wanderly Django Settings — SQLite
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-wanderly-change-this-in-production-2024'
DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = [
    ".onrender.com",
    "localhost",
    "127.0.0.1",
]

INSTALLED_APPS = [
    'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes',
    'django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles',
    'channels','accounts','partners','locations','posts','booking',
    'flights','chat','notifications','reviews','core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'wanderly.urls'
TEMPLATES = [{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.debug','django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
ASGI_APPLICATION = 'wanderly.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
AUTH_USER_MODEL='accounts.User'; LOGIN_URL='/accounts/login/'; LOGIN_REDIRECT_URL='/'; LOGOUT_REDIRECT_URL='/'
AUTH_PASSWORD_VALIDATORS=[{'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},{'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator'},{'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},{'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'}]
LANGUAGE_CODE='en-us'; TIME_ZONE='UTC'; USE_I18N=True; USE_TZ=True
STATIC_URL='/static/'; STATICFILES_DIRS=[BASE_DIR/'static']; STATIC_ROOT=BASE_DIR/'staticfiles'
MEDIA_URL='/media/'; MEDIA_ROOT=BASE_DIR/'media'
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
CHANNEL_LAYERS={'default':{'BACKEND':'channels.layers.InMemoryChannelLayer'}}
WEATHER_API_KEY=os.environ.get('WEATHER_API_KEY',''); WEATHER_API_URL='https://api.openweathermap.org/data/2.5/weather'
AMADEUS_API_KEY=os.environ.get('AMADEUS_API_KEY',''); AMADEUS_API_SECRET=os.environ.get('AMADEUS_API_SECRET','')
POST_LIMIT_PER_PARTNER=5; MAX_IMAGES_PER_POST=5; MAX_PLACES_PER_CITY=20; CHAT_MESSAGE_EXPIRY_DAYS=180
CACHES={'default':{'BACKEND':'django.core.cache.backends.locmem.LocMemCache'}}
EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'; EMAIL_HOST='localhost'; EMAIL_PORT=25
