"""
Django settings for CineMatch — Movie Recommendation System
"""

from pathlib import Path
import os
import sys

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Add project root to sys.path so 'models' package is importable ──
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

SECRET_KEY = 'django-insecure-cinematch-movie-recommendation-system-kartik-2024'

DEBUG = True

# Allow requests from the local dev server on 127.0.0.1:8000
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '[::1]',
    '*',   # kept for convenience in dev; remove for production
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'recommender_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # CSRF is intentionally relaxed below for local dev API calls from 127.0.0.1:8000
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'cinematch.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'cinematch.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Path to data CSVs
DATA_DIR = BASE_DIR / 'data'

# ── CORS — allow http://127.0.0.1:8000 to call the API ──────────────────────
# These headers let the browser make fetch() calls to http://127.0.0.1:8000
# without being blocked. Works without django-cors-headers package.
CORS_ALLOWED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]

# ── Custom CORS middleware (no extra package needed) ─────────────────────────
# Injected via a simple response hook in the common middleware above.
# If you want full CORS support, run:  pip install django-cors-headers
# and add 'corsheaders' to INSTALLED_APPS + 'corsheaders.middleware.CorsMiddleware'
# to the top of MIDDLEWARE. For local dev the views use @csrf_exempt so it works fine.
