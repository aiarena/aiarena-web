from .default import *  # noqa: F403


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-t*4r1u49=a!ah1!z8ydsaajr!lv-f(@r07lm)-9fro_9&67xqd"

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS.append("sslserver")  # noqa: F405
INSTALLED_APPS.append("debug_toolbar")  # noqa: F405
MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405

#################################
# Django Storages & django-private-storage configuration #
#################################

DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"  # TODO: set to local filesystem
PRIVATE_STORAGE_CLASS = "private_storage.storage.s3boto3.PrivateS3BotoStorage"

# PRIVATE_STORAGE_ROOT =  TODO
