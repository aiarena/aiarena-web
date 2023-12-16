import os
from socket import gethostbyname, gethostname

from django.utils.functional import SimpleLazyObject
from django.utils.module_loading import import_string

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from .default import *  # noqa: F403


DEBUG = False

SECRET_KEY = os.environ.get("SECRET_KEY", None)
if SECRET_KEY is None:
    raise Exception("You must set the SECRET_KEY to something secure before running in production or staging.")

ALLOWED_HOSTS = [
    "aiarena-test.net",
    "aiarena.net",
    "sc2ai.com",
    "sc2ai.net",
    "www.sc2ai.net",
    gethostbyname(gethostname()),
]
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_REDIRECT_EXEMPT = [r"^health-check/$"]

################################################################################
# Password validation                                                          #
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators #
################################################################################

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

#######################
# Cache Configuration #
#######################

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": redis_url(REDIS_CACHE_DB),  # noqa F405
    },
    "select2": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": redis_url(REDIS_CACHE_DB),  # noqa F405
        "KEY_PREFIX": "select2",
    },
}


##################
# Email Settings #
##################

DEFAULT_FROM_EMAIL = "AI Arena <noreply@aiarena.net>"
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS")
EMAIL_PORT = os.environ.get("EMAIL_PORT")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")

##########################################################
# Django Storages & django-private-storage configuration #
##########################################################

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
PRIVATE_STORAGE_CLASS = "private_storage.storage.s3boto3.PrivateS3BotoStorage"

AWS_S3_FILE_OVERWRITE = True
AWS_PRIVATE_S3_FILE_OVERWRITE = True

WIKI_STORAGE_BACKEND = SimpleLazyObject(lambda: import_string("storages.backends.s3boto3.S3Boto3Storage")())
WIKI_ATTACHMENTS_LOCAL_PATH = False
WIKI_ATTACHMENTS_APPEND_EXTENSION = False

AWS_STORAGE_BUCKET_NAME = os.environ.get("MEDIA_BUCKET")
AWS_PRIVATE_STORAGE_BUCKET_NAME = os.environ.get("MEDIA_BUCKET")

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")

AWS_S3_REGION_NAME = "eu-central-1"
AWS_S3_OBJECT_PARAMETERS = {"ACL": "private"}
AWS_S3_ADDRESSING_STYLE = "virtual"
AWS_PRIVATE_S3_ADDRESSING_STYLE = "virtual"
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_PRIVATE_S3_SIGNATURE_VERSION = "s3v4"
AWS_PRIVATE_S3_ENCRYPTION = True
AWS_QUERYSTRING_AUTH = True
AWS_QUERYSTRING_EXPIRE = 60 * 60
AWS_LOCATION = "media/"
AWS_PRIVATE_LOCATION = "private-media/"

# Sentry configuration
SENTRY_DSN = os.environ.get("SENTRY_DSN")
BUILD_NUMBER = os.environ.get("BUILD_NUMBER")
if SENTRY_DSN:
    sentry_kwargs = {
        "dsn": SENTRY_DSN,  # noqa: F405
        "integrations": [
            CeleryIntegration(),
            DjangoIntegration(),
            RedisIntegration(),
        ],
        "release": BUILD_NUMBER,
        "send_default_pii": True,
        # https://docs.sentry.io/performance/distributed-tracing/#python
        "traces_sample_rate": 1.0,
        "attach_stacktrace": True,
    }
    sentry_sdk.init(**sentry_kwargs)
