from .default import *  # noqa: F403


DEBUG = True
DJDT = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-t*4r1u49=a!ah1!z8ydsaajr!lv-f(@r07lm)-9fro_9&67xqd"

ALLOWED_HOSTS = ["*"]

#################################
# Django Storages & django-private-storage configuration #
#################################

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
PRIVATE_STORAGE_CLASS = "private_storage.storage.files.PrivateFileSystemStorage"
PRIVATE_STORAGE_ROOT = os.path.join(BASE_DIR, "private-media")  # noqa: F405
MEDIA_ROOT = os.path.join(BASE_DIR, "media")  # noqa: F405

if RUNNING_TESTS:  # noqa: F405
    # Tests use production's S3 storage, against a fake S3 (moto) started for each test in the root conftest.
    STORAGES = {
        "default": {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
    PRIVATE_STORAGE_CLASS = "private_storage.storage.s3boto3.PrivateS3BotoStorage"
    AWS_STORAGE_BUCKET_NAME = "test-media-bucket"
    AWS_PRIVATE_STORAGE_BUCKET_NAME = "test-media-bucket"
    AWS_ACCESS_KEY_ID = "testing"
    AWS_SECRET_ACCESS_KEY = "testing"

DJANGO_VITE["default"]["dev_mode"] = not RUNNING_TESTS  # noqa: F405
DJANGO_VITE["default"]["dev_server_port"] = 4000  # noqa: F405
