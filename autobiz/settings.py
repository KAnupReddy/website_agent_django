"""
Django settings for the AutoBiz AI project.

All environment-specific values are read from a `.env` file in the project
root (see `.env.example`).
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')


def env(key, default=''):
    return os.getenv(key, default)


def env_bool(key, default=False):
    return env(key, str(default)).strip().lower() in ('1', 'true', 'yes', 'on')


# ─── Core ──────────────────────────────────────────────────────────────────

SECRET_KEY = env('DJANGO_SECRET_KEY', 'django-insecure-change-me-in-production')
DEBUG = env_bool('DJANGO_DEBUG', True)
ALLOWED_HOSTS = [h.strip() for h in env('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if h.strip()]
CSRF_TRUSTED_ORIGINS = [o.strip() for o in env('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'dashboard',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'autobiz.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'autobiz.wsgi.application'


# ─── Database ──────────────────────────────────────────────────────────────
# DB_ENGINE: sqlite (default) | mysql | mysql_legacy
#   mysql        → MySQL 8.4+ / MariaDB 10.11+ (what Django 6 officially supports)
#   mysql_legacy → same driver, but allows older servers such as XAMPP's MariaDB 10.4

DB_ENGINE = env('DB_ENGINE', 'sqlite').lower()

if DB_ENGINE in ('mysql', 'mysql_legacy'):
    DATABASES = {
        'default': {
            'ENGINE': 'autobiz.db.mysql_legacy' if DB_ENGINE == 'mysql_legacy' else 'django.db.backends.mysql',
            'NAME': env('DB_NAME', 'autobiz_ai_django'),
            'USER': env('DB_USER', 'root'),
            'PASSWORD': env('DB_PASSWORD', ''),
            'HOST': env('DB_HOST', '127.0.0.1'),
            'PORT': env('DB_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / env('DB_NAME', 'db.sqlite3'),
        }
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# The original CodeIgniter database — only read by `manage.py import_legacy`
LEGACY_DB = {
    'NAME': env('LEGACY_DB_NAME', 'autobiz_ai'),
    'USER': env('LEGACY_DB_USER', 'root'),
    'PASSWORD': env('LEGACY_DB_PASSWORD', ''),
    'HOST': env('LEGACY_DB_HOST', '127.0.0.1'),
    'PORT': int(env('LEGACY_DB_PORT', '3306') or 3306),
}


# ─── Auth ──────────────────────────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ─── i18n / static ─────────────────────────────────────────────────────────

LANGUAGE_CODE = 'en-us'
TIME_ZONE = env('TIME_ZONE', 'UTC')
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'


# ─── AutoBiz ───────────────────────────────────────────────────────────────

WRITABLE_DIR = BASE_DIR / 'writable'
BUILD_DIR = WRITABLE_DIR / 'builds'

OPENAI_API_KEY = env('OPENAI_API_KEY')
OPENAI_MODEL = env('OPENAI_MODEL', 'gpt-4o')

HOSTING = {
    'BASE_DOMAIN': env('HOSTING_BASE_DOMAIN', 'localhost'),
    'FTP_HOST': env('HOSTING_FTP_HOST'),
    'FTP_USER': env('HOSTING_FTP_USER'),
    'FTP_PASS': env('HOSTING_FTP_PASS'),
    'FTP_ROOT': env('HOSTING_FTP_ROOT', '/public_html/demos/'),
}

APIFY_API_TOKEN = env('APIFY_API_TOKEN')


# ─── Email (SMTP, used by the Outreach agent) ──────────────────────────────

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(env('EMAIL_PORT', '587') or 587)
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
_crypto = env('EMAIL_CRYPTO', 'tls').lower()
EMAIL_USE_TLS = _crypto == 'tls'
EMAIL_USE_SSL = _crypto == 'ssl'
EMAIL_TIMEOUT = 30
OUTREACH_FROM_EMAIL = env('EMAIL_FROM', EMAIL_HOST_USER)
OUTREACH_FROM_NAME = env('EMAIL_FROM_NAME', 'AutoBiz AI')
DEFAULT_FROM_EMAIL = f'{OUTREACH_FROM_NAME} <{OUTREACH_FROM_EMAIL}>' if OUTREACH_FROM_EMAIL else 'webmaster@localhost'


# ─── Logging ───────────────────────────────────────────────────────────────

(WRITABLE_DIR / 'logs').mkdir(parents=True, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {'format': '%(levelname)s - %(asctime)s --> %(message)s'},
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'default'},
        'file': {
            'class': 'logging.FileHandler',
            'filename': WRITABLE_DIR / 'logs' / 'autobiz.log',
            'encoding': 'utf-8',
            'formatter': 'default',
        },
    },
    'loggers': {
        'autobiz': {'handlers': ['console', 'file'], 'level': 'INFO'},
    },
}
