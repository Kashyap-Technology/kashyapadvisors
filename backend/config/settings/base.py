from pathlib import Path
import environ
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR.parent / '.env')
DEBUG = env('DEBUG')
SECRET_KEY = env('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])
PUBLIC_SITE_URL = env('PUBLIC_SITE_URL', default='https://kashyapadvisors.com')
INSTALLED_APPS = ['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','rest_framework','platform_app']
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware','whitenoise.middleware.WhiteNoiseMiddleware','config.cors.CorsMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF = 'config.urls'
TEMPLATES = [{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION = 'config.wsgi.application'
DATABASES = {'default':env.db('DATABASE_URL',default='postgres://kashyap:kashyap@localhost:5432/kashyap')}
AUTH_PASSWORD_VALIDATORS = [{'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},{'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator'},{'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},{'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'}]
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kathmandu'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
STORAGES = {'default':{'BACKEND':'django.core.files.storage.FileSystemStorage'},'staticfiles':{'BACKEND':'whitenoise.storage.CompressedManifestStaticFilesStorage'}}
if env.bool('USE_STORJ',default=False):
    STORAGES['default'] = {'BACKEND':'storages.backends.s3.S3Storage','OPTIONS':{'access_key':env('STORJ_ACCESS_KEY'),'secret_key':env('STORJ_SECRET_KEY'),'bucket_name':env('STORJ_BUCKET'),'endpoint_url':env('STORJ_ENDPOINT',default='https://gateway.storjshare.io'),'region_name':'us-east-1','default_acl':None,'querystring_auth':True,'file_overwrite':False}}
REST_FRAMEWORK = {'DEFAULT_PERMISSION_CLASSES':['rest_framework.permissions.AllowAny'],'DEFAULT_THROTTLE_CLASSES':['rest_framework.throttling.AnonRateThrottle'],'DEFAULT_THROTTLE_RATES':{'anon':'120/minute','submissions':'10/hour'},'DEFAULT_RENDERER_CLASSES':['rest_framework.renderers.JSONRenderer']}
EMAIL_BACKEND = env('EMAIL_BACKEND',default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST',default='localhost')
EMAIL_PORT = env.int('EMAIL_PORT',default=587)
EMAIL_HOST_USER = env('EMAIL_HOST_USER',default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD',default='')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS',default=True)
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL',default='website@kashyapadvisors.com')
NOTIFICATION_EMAIL = env('NOTIFICATION_EMAIL',default='')
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS',default=['http://localhost:5173','http://127.0.0.1:5173'])
DATA_UPLOAD_MAX_MEMORY_SIZE = 6 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
