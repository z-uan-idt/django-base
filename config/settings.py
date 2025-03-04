from pathlib import Path
from decouple import Csv
from decouple import config
from decouple import Choices
from datetime import timedelta


BASE_DIR = Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default=[], cast=Csv())

SECRET_KEY = config("SECRET_KEY", default="", cast=str)

DEBUG = config("DEBUG", default=False, cast=bool)

INSTALLED_APPS = [
    "drf_yasg",
    "corsheaders",
    "rest_framework",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.user",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "utils.exception.ExceptionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'django_currentuser.middleware.ThreadLocalUserMiddleware',
]

REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "utils.exception.ExceptionHandler",
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_AUTHENTICATION_CLASSES": ["utils.authentication.AuthenticationDefault"],
}

CORS_ORIGIN_ALLOW_ALL = True

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "USER": config("POSTGRES_USER", cast=str),
        "HOST": config("POSTGRES_HOST", cast=str),
        "PORT": config("POSTGRES_PORT", cast=str),
        "NAME": config("POSTGRES_DBNAME", cast=str),
        "PASSWORD": config("POSTGRES_PASS", cast=str),
    }
}

REDIS_HOST = config("REDIS_HOST", default=None, cast=str)

REDIS_PORT = config("REDIS_PORT", default=None, cast=str)

redis_db_choices = Choices([i for i in range(1, 16)], cast=int)

REDIS_DB = config("REDIS_DB", default=1, cast=redis_db_choices)

if REDIS_HOST is not None and REDIS_PORT is not None:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        }
    }

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

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

TIME_ZONE = "Asia/Ho_Chi_Minh"

STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "static"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "users.User"

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
        }
    },
    "USE_SESSION_AUTH": False,
    "FORCE_SCRIPT_NAME": "/",
    "DOC_EXPANSION": "none",
}

env_name = ["development", "test", "staging", "production"]

env_choices = Choices(env_name, cast=str)

ENV = config("ENV", default=1, cast=env_choices)

IS_DEV = ENV == "development"

IS_TEST = ENV == "test"

IS_STAGING = ENV == "staging"

IS_PROD = ENV == "production"

ACCESS_TOKEN_LIFETIME = config("ACCESS_TOKEN_LIFETIME", cast=int, default=5)

REFRESH_TOKEN_LIFETIME = config("REFRESH_TOKEN_LIFETIME", cast=int, default=30)

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=ACCESS_TOKEN_LIFETIME),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=REFRESH_TOKEN_LIFETIME),
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=ACCESS_TOKEN_LIFETIME),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=REFRESH_TOKEN_LIFETIME),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
}

DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50 MB

FILE_UPLOAD_MAX_MEMORY_SIZE = DATA_UPLOAD_MAX_MEMORY_SIZE

DEFAULT_FILE_STORAGE = 'utils.b2_storage.storage.B2Storage'

BACKBLAZEB2_APP_KEY_ID = config("BACKBLAZEB2_APP_KEY_ID", cast=str, default="")

BACKBLAZEB2_APP_KEY = config("BACKBLAZEB2_APP_KEY", cast=str, default="")

BACKBLAZEB2_BUCKET_NAME = config("BACKBLAZEB2_BUCKET_NAME", cast=str, default="")

BACKBLAZEB2_BUCKET_ID = config("BACKBLAZEB2_BUCKET_ID", cast=str, default="")

BACKBLAZEB2_ACCOUNT_ID = config("BACKBLAZEB2_ACCOUNT_ID", cast=str, default="")

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = config("EMAIL_HOST")

EMAIL_USE_TLS = config("EMAIL_USE_TLS")

EMAIL_PORT = config("EMAIL_PORT")

EMAIL_HOST_USER = config("EMAIL_HOST_USER")

EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")