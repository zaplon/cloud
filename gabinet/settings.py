# -*- coding: utf-8 -*-
"""
Django settings for gabinet project.

Generated by 'django-admin startproject' using Django 1.10.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

# BASE_DIR = PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR =  PROJECT_DIR = '/app/'
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '9pc#_y&@a7t#z^n6y59m#x7k+4)kp4s0ob_ha(=1!8a4_72aa6'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['0.0.0.0', 'localhost', '127.0.0.1']

# Application definition

INSTALLED_APPS = [
    # 'material.theme.indigo',
    # 'material',
    # 'material.admin',
    # 'jet',
    # 'jet_django',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'account',
    'crispy_forms',
    'g_utils',
    'user_profile',
    'visit',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'timetable',
    'medicine',
    'result',
    'forms',
    'examination',
    'misal',
    'wkhtmltopdf',
    'administration',
    'pinax_theme_bootstrap',
    'bootstrapform',
    "compressor",
    "debug_toolbar",
    "agreements",
    'corsheaders',
    # 'django_mfa'
]
SITE_ID = 1
MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'g_utils.middleware.permissions_middleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "account.middleware.LocaleMiddleware",
    "account.middleware.TimezoneMiddleware",
    # 'django_mfa.middleware.MfaMiddleware'
    # "agreements.middleware.display_agreement_middleware"
]

ROOT_URLCONF = 'gabinet.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "g_utils.context_processors.utils",
                "account.context_processors.account",
                "g_utils.context_processors.form_helpers",
                # "pinax_theme_bootstrap.context_processors.theme"
            ],
        },
    },
]

WSGI_APPLICATION = 'gabinet.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db2.sqlite3'),
    },
    'medicines': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'medicines.sqlite3')
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': 'memcached:11211',
    }
}

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

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False
TIME_ZONE = 'Europe/Warsaw'

LOGIN_URL = '/account/login/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/account/login/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'public', 'static')

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder'
]

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

BOWER_INSTALLED_APPS = (
    'bootstrap#v4.0.0-alpha.5',
    'knockoutjs',
    'fullcalendar',
    'jquery-ui',
    'bootstrap-select',
    'chart.js'
)

CRISPY_TEMPLATE_PACK = 'bootstrap4'

MEDIA_ROOT = os.path.join(BASE_DIR, 'public', 'media')
MEDIA_URL = '/media/'
STATIC_URL = '/assets/'

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'g_utils.rest.GabinetPagination',
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'PAGE_SIZE': 10
}

LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]
LANGUAGE_CODE = 'pl'
VISIT_TABS_DIR = os.path.join(BASE_DIR, 'templates', 'visit', 'tabs')
APP_URL = 'http://127.0.0.1:8001/'

MODULES = [
    (True, 'stats', u'Statystyki'),
    (['timetable.change_term', 'visit.change_visit'], 'calendar', u'Kalendarz'),
    ('user_profile.change_patient', 'patients', u'Lista pacjentów'),
    (True, 'archive', u'Archiwum'),
    (True, 'medicines', u'Lista leków'),
    ('medicine.change_prescription', 'prescriptions', u'Lista recept'),
    (True, 'icd10', u'Kody ICD-10'),
    ('user_profile.change_template', 'templates', u'Szablony'),
    ('visit.change_tab', 'tabs', u'Zakładki'),
    ('timetable.change_service', 'services', u'Usługi'),
    ('timetable.change_localization', 'localizations', u'Lokalizacje'),
    ('auth.change_user', 'users', u'Użytkownicy'),
    (True, 'forms', u'Formularze'),
    ('user_profile.change_system_settings', 'settings', u'Ustawienia'),
    ('visit.change_visit', 'visits', u'Wizyty')
]

# misal settings
MISAL_SETUP = True
GENERATE_TERMS = True
USE_ELO = False
USE_SMS_LOGIN = False
SIMULATE_SMS_LOGIN = True

DATABASE_ROUTERS = ['medicine.router.MedicineRouter']

EXTENSIONS = {'img': ['jpg', 'png', 'bnp', 'gif'], 'video': ['mp3', 'wav']}

ELASTIC_HOST = 'elasticsearch'
DATE_FORMAT = '%d-%m-%Y'
COMPRESS_ENABLED = False
COMPRESS_OFFLINE = True
INTERNAL_IPS = ['127.0.0.1', 'localhost']
SESSION_COOKIE_AGE = 7200
CSRF_COOKIE_SECURE = False
CORS_ORIGIN_WHITELIST = (
    'localhost:8081',
    'gabinet'
)

OLD_PASSWORD_FIELD_ENABLED = True
