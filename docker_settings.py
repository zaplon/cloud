from gabinet.settings import *


WKHTMLTOPDF_CMD = '/app/bin/wkhtmltox/bin/wkhtmltopdf'
APP_URL = 'http://127.0.0.1:8080/'
ALLOWED_HOSTS = ALLOWED_HOSTS + ['gabinet']
BASE_DIR = '/app/'
STATIC_ROOT = os.path.join(BASE_DIR, 'public', 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'public', 'media')
