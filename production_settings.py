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
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'medicines.sqlite3')
    }
}

ELASTIC_HOST = 'elastic1'
ALLOWED_HOSTS = ['doktor.misal.pl', 'localhost', 'gabinet', '10.0.0.157', '10.198.0.2', '10.0.2.199']
APP_URL = 'http://gabinet/'
DEBUG = True
COMPRESS_ENABLED = True
BASE_DIR = '/app/'
STATIC_ROOT = os.path.join(BASE_DIR, 'public', 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'public', 'media')
WKHTMLTOPDF_CMD = '/app/bin/wkhtmltox/bin/wkhtmltopdf'
CORS_ORIGIN_WHITELIST = (
    'localhost:8081',
    'gabinet',
    '10.198.0.2',
    '10.0.0.157',
    '10.0.2.199'
)
