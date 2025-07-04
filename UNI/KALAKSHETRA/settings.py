"""
Django settings for KALAKSHETRA project.

Generated by 'django-admin startproject' using Django 5.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""
import ast
import datetime
import json
import os
from pathlib import Path
import environ
from boto3 import session as boto3_session

# from .loggers import *

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment variables setup
env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, "django-insecure-1^l_%acdj@6es-cjp#i()q2t*1sj(j2d!=c-mhl5o-vgg90fpq"),
    ALLOWED_HOSTS=(list, ['*']),
    AWS_STORAGE_BUCKET_NAME=(str, ''),
    AWS_S3_REGION_NAME=(str, 'ap-south-1'),
    USE_S3=(bool, False),
    DOMAIN_NAME=(str, ''),
    SITE_URL=(str, ''),
)

# ALLOWED_HOSTS = ['*']

# Read .env.development file if it exists
environ.Env.read_env(os.path.join(BASE_DIR, '.env.development'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# Application definition
PREDEFINED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

CORE_APPS = [
    "user_details",
    "apps.users",
    "apps.meta_app",
    "axes",
    "apps.master_data",
    "apps.production_house",
    "apps.movies",
    "apps.budget",
    "apps.event",
    "apps.blogs",
    'ckeditor',
    "apps.blog",
    "apps.web_pages",
    "apps.staticpages",
    "apps.configurations",
    'storages',
    'apps.payments',
    'apps.schedule',
    'apps.hospital',
    'apps.doctors',
]
INSTALLED_APPS = PREDEFINED_APPS + CORE_APPS

# CKEDITOR_BASEPATH = "/static/ckeditor/ckeditor/"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'axes.middleware.AxesMiddleware',
]

ROOT_URLCONF = "KALAKSHETRA.urls"

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
    },
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "KALAKSHETRA.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    # 'default': {
    #     'ENGINE': env('DBENGINE'),
    #     'NAME': env('DATABASE'),
    #     'USER': env('DBUSER'),
    #     'PASSWORD': env('DBPASSWORD'),
    #     'HOST': env('DBHOST'),
    #     'PORT': env('PORT'),
    # }
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'uni_test',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True

# Optional: Apply format to admin views even if localization is off
USE_L10N = False

# Optional: Customize time and date format (applies to templates using |date:"DATETIME_FORMAT")
DATETIME_FORMAT = 'd M Y, H:i:s'  # e.g., "10 May 2025, 14:30:00"
DATE_FORMAT = 'd M Y'  # e.g., "10 May 2025"
TIME_FORMAT = 'H:i:s'  # e.g., "14:30:00"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# STATIC_URL = "static/"
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# from storages.backends.s3boto3 import S3Boto3Storage
#
# class StaticStorage(S3Boto3Storage):
#     location = 'static'  # This folder inside your S3 bucket where static files will be stored
#     default_acl = 'public-read'  # Optional, set default access permissions
# S3 Configuration for static files
if env('USE_S3'):
    # AWS settings
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', default='')
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', default='')
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME', default='kalakshetra-dev-static-files')
    AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME')
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}

    # S3 static settings
    STATIC_LOCATION = 'static'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/'
    # STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    # DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
    STATICFILES_STORAGE = 'KALAKSHETRA.settings.s3boto3.S3Boto3Storage'

S3_SESSION = boto3_session.Session(region_name=AWS_S3_REGION_NAME)
S3_CLIENT = S3_SESSION.client(
    's3', config=boto3_session.Config(signature_version='s3v4'))
# S3_CLIENT = S3_SESSION.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
#                               aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
#                               region_name=AWS_SNS_REGION_NAME)

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Security settings for production
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'

    # Domain settings
    DOMAIN_NAME = env('DOMAIN_NAME')
    SITE_URL = env('SITE_URL')

    # Update CSRF settings for the domain
    if DOMAIN_NAME:
        CSRF_COOKIE_DOMAIN = DOMAIN_NAME
        # CSRF_TRUSTED_ORIGINS = [f"https://{DOMAIN_NAME}", f"https://www.{DOMAIN_NAME}"]

RUN_SERVER_PORT = 8080
AUTH_USER_MODEL = 'user_details.User'

exceptions_mapping_file = open(os.path.join(BASE_DIR, 'utils/exceptions_mapping.json'), "r")
EXCEPTIONS_MAPPING = json.loads(exceptions_mapping_file.read())
exceptions_mapping_file.close()

AUTHENTICATION_BACKENDS = (
    # 'django.contrib.auth.backends.ModelBackend',
    'axes.backends.AxesBackend',
    'utils.custom_authentication.CustomPatientAuthBackend',
)

JWT_AUTH = {
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=90),
    'JWT_ALLOW_REFRESH': True,
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=90),
}

REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
    ),

    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'EXCEPTION_HANDLER': 'utils.exception_handler.custom_exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'utils.custom_pagination.CustomPagination',
    'PAGE_SIZE': 15
}

CSRF_TRUSTED_ORIGINS = [
    'https://api.dev.cineartery.com',
    'http://api.dev.cineartery.com',
    'https://www.cineartery.com',
    'http://www.cineartery.com',
    'https://cineartery.com',
    'http://cineartery.com',
]

VALID_IMAGE_FILE_EXTENSIONS = ast.literal_eval(os.getenv('VALID_IMAGE_FILE_EXTENSIONS', default=''))
MAX_FILE_UPLOAD_SIZE = int(env('MAX_FILE_UPLOAD_SIZE_IN_MB', default=''))

AXES_FAILURE_LIMIT = 3
AXES_COOLOFF_TIME = datetime.timedelta(minutes=1)
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True
AXES_USERNAME_FORM_FIELD = 'mobile'

MAX_PAGINATION_SIZE = 10
HARDCODED_MOBILE_NO = +919880000300
HARDCODED_MOBILE_OTP = '1234'
IS_PRODUCTION = False
OTP_LENGTH = 4
OTP_CHARACTERS = '0123456789'
OTP_EXPIRATION_TIME = 300
PAGE_SIZE = 15
RAZORPAY_KEY_ID = env('RAZORPAY_KEY_ID', default='')
RAZORPAY_KEY_SECRET = env('RAZORPAY_KEY_SECRET', default='')
BED_BASE_URL = env('BED_BASE_URL', default='')
