from __future__ import unicode_literals
import os
"""
Django settings for tests project.
"""

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = '=)c(th7-3@w*n9mf9_b+2qg685lc6qgfars@yu1g516xu5&is)'

DEBUG = True

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.messages',
    'django.contrib.flatpages',
    'djangoseo',
    'tests.userapp',
)

MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'djangoseo.middleware.RedirectFallbackMiddleware',
    'djangoseo.middleware.RedirectsMiddleware'
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages'
            ]
        }
    }
]

ROOT_URLCONF = 'tests.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'djseo',
        'USER': 'postgres',
    }
}

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

SITE_ID = 1

CACHE_BACKEND = 'dummy://'
# Enable when testing cache
# CACHE_BACKEND = "locmem://?timeout=30&max_entries=400"

SEO_MODELS = ('userapp',)

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

SEO_USE_REDIRECTS = True
SEO_TRACKED_MODELS = ('tests.userapp.models.Page',)

try:
    from settings_local import *
except ImportError:
    pass
