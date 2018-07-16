from gabinet.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gabinet',
        'HOST': 'mysql',
        'USER': 'root',
        'PASSWORD': ''
    },
    'medicines': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'medicines',
        'USER': 'root',
        'HOST': 'mysql',
        'PASSWORD': ''
    }
}

ELASTIC_HOST = 'elastic1'
ALLOWED_HOSTS = ['doktor.misal.pl', 'localhost', 'gabinet']
APP_URL = 'http://gabinet/'
DEBUG = True
COMPRESS_ENABLED = True
BASE_DIR = '/app/'
STATIC_ROOT = os.path.join(BASE_DIR, 'public', 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'public', 'media')
WKHTMLTOPDF_CMD = 'docker-compose run --rm wkhtmltopdf'
