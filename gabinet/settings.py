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
BASE_DIR = PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '9pc#_y&@a7t#z^n6y59m#x7k+4)kp4s0ob_ha(=1!8a4_72aa6'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'account',
    'djangobower',
    'crispy_forms',
    'g_utils',
    'user_profile',
    'visit',
    'dashboard',
    'rest_framework',
    'timetable',
    'medicine',
    'result',
    'forms',
    'wkhtmltopdf'
]
SITE_ID = 1
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'g_utils.middleware.setup_middleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "account.middleware.LocaleMiddleware",
    "account.middleware.TimezoneMiddleware"
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

LANGUAGE_CODE = 'pl-pl'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True
TIME_ZONE = 'Europe/Warsaw'

LOGIN_URL = '/account/login/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/account/login/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'public', 'static')

BOWER_COMPONENTS_ROOT = os.path.join(BASE_DIR, 'components')

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'djangobower.finders.BowerFinder'
]

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'), os.path.join(BASE_DIR, 'frontend', 'static')]

BOWER_INSTALLED_APPS = (
    'bootstrap#v4.0.0-alpha.5',
    'knockoutjs',
    'fullcalendar',
    'jquery-ui'
)

CRISPY_TEMPLATE_PACK = 'bootstrap4'

MEDIA_ROOT = os.path.join(BASE_DIR, 'public', 'media')
MEDIA_URL = '/media/'

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination'
}

LANGUAGE_CODE = 'pl-pl'
VISIT_TABS_DIR = os.path.join(BASE_DIR, 'templates', 'visit', 'tabs')
WKHTMLTOPDF_CMD = '/home/jan/wkhtmltox/bin/wkhtmltopdf'
APP_URL = 'http://localhost:8001/'

MODULES = [
    (['timetable.change_term', 'visit.change_visit'], 'calendar', u'Kalendarz'),
    ('user_profile.change_patient', 'patients', u'Lista pacjentów'),
    (True, 'archive', u'Archiwum'),
    (True, 'medicines', u'Lista leków'),
    (True, 'icd10', u'Kody ICD-10'),
    ('visit.change_visit', 'templates', u'Szablony'),
    ('visit.change_tab', 'tabs', u'Zakładki'),

]

# misal settings
MISAL_SETUP = True
GENERATE_TERMS = False
USE_ELO = True
USE_SMS_LOGIN = True
SIMULATE_SMS_LOGIN = True

DATABASE_ROUTERS = ['medicine.router.MedicineRouter']
