import json
import os
import subprocess
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if 'DOMAIN' not in os.environ:
    export = subprocess.check_output(['bash', '-c', 'source .env && ./venv/bin/python project_conf/env.py raw'],
                                     cwd=BASE_DIR)
    for key, value in json.loads(export.decode('utf-8')).items():
        os.environ[key] = value

from .env import environ

SECRET_KEY = 'zsutuls@j2m^^+q-9(05wh4u8*v0xw#x78l^kc(b0t6x#aplae'

DEBUG = environ['DJANGO_DEBUG']

DOMAIN = environ['DOMAIN']

ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = [DOMAIN]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'project_name',

    'api',

    'easy_thumbnails',
    'robust',
    'happymailer',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
]

ROOT_URLCONF = 'project_conf.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
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

WSGI_APPLICATION = 'project_conf.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
DB = {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'HOST': environ['DATABASE_HOST'],
    'NAME': environ['DATABASE_NAME'],
    'USER': environ['DATABASE_USER'],
    'PASSWORD': environ['DATABASE_PASSWORD'],
    'ATOMIC_REQUESTS': True,
}

DATABASES = {
    'default': DB,
    'robust_ratelimit': DB,
}

AUTH_USER_MODEL = 'project_name.User'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

USE_ETAGS = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = environ.get('STATIC_URL', '/static/')
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = environ.get('MEDIA_URL', '/media/')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'build'),
    os.path.join(BASE_DIR, 'www-root'),
]

# Sessions

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

# Superusers

SUPERUSERS = environ['SUPERUSERS']
SUPERUSER_DEFAULT_PASSWORD = environ['SUPERUSER_PASSWORD']

# Logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'formatters': {
        'verbose': {
            'format':
                '%(levelname)s|%(asctime)s|%(name)s>> %(message)s',
        },
        'color': {
            '()': 'colorlog.ColoredFormatter',
            'format': '%(log_color)s%(levelname)-8s %(message)s',
            'log_colors': {
                'DEBUG': 'bold_black',
                'INFO': 'white',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            },
        }
    },
    'handlers': {
        'colored': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'color'
        },
        'plain': {
            'level': 'WARNING',
            'filters': ['require_debug_false'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        '': {
            'handlers': ['colored', 'plain'],
            'level': 'DEBUG',
        },
        'py.warnings': {
            'level': 'DEBUG',
        },
    }
}

# Emails

EMAIL_CONFIRMATION = True
EMAIL_SKIP = False
EMAIL_EXCLUDE_LIST = environ['EMAIL_EXCLUDE_LIST']

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

if environ.get('EMAIL_BACKEND'):
    EMAIL_BACKEND = environ['EMAIL_BACKEND']

# Api

API_DEFAULT_ROUTER = 'project_name.api.router'


# Happymailer

HAPPYMAILER_BACKEND = 'happymailer.backends.MjmlBackend'
HAPPYMAILER_MJML_BIN = [os.path.join(BASE_DIR, './node_modules/.bin/mjml')]
HAPPYMAILER_FROM = None

# Easy-Thumbnails

AVATAR_ALIASES = {
    'x80': {'size': (80, 80), 'crop': True},
    'x300': {'size': (300, 300), 'crop': True},
}

THUMBNAIL_ALIASES = {
    'project_name.User.avatar_image': AVATAR_ALIASES,
}

THUMBNAIL_NAMER = 'easy_thumbnails.namers.source_hashed'


# Django-Robust

ROBUST_LOG_EVENTS = True

ROBUST_WORKER_FAILURE_TIMEOUT = 5

ROBUST_NOTIFY_TIMEOUT = 10

ROBUST_ALWAYS_EAGER = False

ROBUST_SCHEDULE = [
    (timedelta(minutes=5), 'robust.utils.cleanup'),
]


# Debug Mode

if DEBUG:
    INTERNAL_IPS = (
        '127.0.0.1', '33.33.33.1', '192.168.121.1',
    )

