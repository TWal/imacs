from os import environ
from .app_settings import *

SECRET_KEY=environ.get('SECRET_KEY')
STATIC_ROOT=environ.get('STATIC_ROOT')
ALLOWED_HOSTS = list(environ.get('ALLOWED_HOSTS', default='').split(','))
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': environ.get('DB_NAME'),
        'HOST': '',
    }
}
DEBUG = False
