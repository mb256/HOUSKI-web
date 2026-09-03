from .base import *
from decouple import config, Csv

DEBUG = False
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

SECRET_KEY = config('SECRET_KEY')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security headers
SECURE_SSL_REDIRECT = False    # PythonAnywhere handles HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
