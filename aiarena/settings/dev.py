import mimetypes

from .default import *  # noqa: F403


DEBUG = True
DJDT = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-t*4r1u49=a!ah1!z8ydsaajr!lv-f(@r07lm)-9fro_9&67xqd"

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS.append("sslserver")  # noqa: F405

#################################
# Django Storages & django-private-storage configuration #
#################################

DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
PRIVATE_STORAGE_CLASS = "private_storage.storage.files.PrivateFileSystemStorage"
PRIVATE_STORAGE_ROOT = os.path.join(BASE_DIR, "private-media")  # noqa: F405
MEDIA_ROOT = os.path.join(BASE_DIR, "media")  # noqa: F405

DJANGO_VITE["default"]["dev_mode"] = True  # noqa: F405
DJANGO_VITE["default"]["dev_server_port"] = 4000  # noqa: F405
