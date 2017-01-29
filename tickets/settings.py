# -*- coding: utf-8 -*-

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import socket
# request.path in templates:
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

if socket.gethostname() == os.environ["DJANGO_PRODUCTION_DOMAIN"]:
    DEBUG = False
    TEMPLATE_DEBUG = False
    ALLOWED_HOSTS = ['*']
    # SSL/HTTPS
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    DEBUG = True
    TEMPLATE_DEBUG = True

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'main',
)

TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'tickets.urls'

WSGI_APPLICATION = 'tickets.wsgi.application'

# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'
STATIC_ROOT = os.environ["DJANGO_STATIC_ROOT"]

STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'), )

MEDIA_URL = '/media/'
MEDIA_ROOT = os.environ["DJANGO_MEDIA_ROOT"]

# On login do not redirect to "/accounts/profile/" but "/inbox/"
LOGIN_REDIRECT_URL = "/inbox/"

# in urls.py the function "logout_then_login" is used to log out
# changing the default value from "/accounts/login/" to "/"
LOGIN_URL = "/"

# Django Crispy Forms
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# Define who gets code error notifications.
# When DEBUG=False and a view raises an exception,
# Django will email these people with the full exception information.
ADMINS = ((os.environ["DJANGO_ADMIN_NAME"],
           os.environ["DJANGO_ADMIN_EMAIL"]), )

# Specifies who should get broken link notifications when
# BrokenLinkEmailsMiddleware is enabled.
MANAGERS = ((os.environ["DJANGO_ADMIN_NAME"],
             os.environ["DJANGO_ADMIN_EMAIL"]), )

# Email delivery to local Postfix-Installation
EMAIL_HOST = os.environ["DJANGO_EMAIL_HOST"]
EMAIL_HOST_USER = os.environ["DJANGO_EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = os.environ["DJANGO_EMAIL_HOST_PASSWORD"]

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s \
                       [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.environ["DJANGO_LOG_FILE"],
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'main': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    }
}
