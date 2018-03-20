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
DEBUG = True
COMPRESS_ENABLED = True
