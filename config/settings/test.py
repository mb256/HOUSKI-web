from .base import *

DEBUG = False

DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': ':memory:',
}

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

SUMMERNOTE_CONFIG = {**SUMMERNOTE_CONFIG, 'attachment_require_authentication': True}
