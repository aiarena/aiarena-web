"""
Django settings for aiarena project.

Generated by 'django-admin startproject' using Django 2.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import sys
from datetime import timedelta
from enum import Enum

from aiarena.core.utils import Elo, EnvironmentType

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR = os.path.dirname(os.path.abspath(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 't*4r1u49=a!ah1!z8ydsaajr!lv-f(@r07lm)-9fro_9&67xqd'

# Flag whether we're in testing mode
# Checks that the second argument is the test command.
TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1']

INTERNAL_IPS = ['127.0.0.1']

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'aiarena',
        'USER': 'aiarena',
        'PASSWORD': 'aiarena',
        'HOST': 'localhost',  # Or an IP Address that your DB is hosted on
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        # todo: having this enabled will open a transaction for every request and therefore slow down the site
        # todo: ideally we will eventually remove this and specify each individual view that needs its own transaction.
        'ATOMIC_REQUESTS': True,
    }
}

# Application definition

INSTALLED_APPS = [
    'registration',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'avatar',
    'aiarena.core',
    'aiarena.frontend',
    'aiarena.api',
    'aiarena.patreon',
    'private_storage',
    'django.contrib.sites.apps.SitesConfig',
    'django.contrib.humanize.apps.HumanizeConfig',
    'django_nyt.apps.DjangoNytConfig',
    'mptt',
    'sekizai',
    'sorl.thumbnail',
    'wiki.apps.WikiConfig',
    'wiki.plugins.attachments.apps.AttachmentsConfig',
    'wiki.plugins.notifications.apps.NotificationsConfig',
    'wiki.plugins.images.apps.ImagesConfig',
    'wiki.plugins.macros.apps.MacrosConfig',
    'wiki.plugins.help.apps.HelpConfig',
    'constance',
    'constance.backends.database',  # this should be removed by any env.py file overriding the constance backend
    'debug_toolbar',  # This will be removed automatically in non-development environments
    'discord_bind',
    'sslserver',  # This will be removed automatically in non-development environments
]

MIDDLEWARE = [
    # This will be removed automatically in non-development environments
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'aiarena.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(APP_DIR, 'frontend/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'constance.context_processors.config',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'aiarena.frontend.context_processors.stats',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                "sekizai.context_processors.sekizai",
            ],
        },
    },
]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 100
}

# Constance https://github.com/jazzband/django-constance
# !IMPORTANT! If you override this setting in an env.py,
# don't forget to remove 'constance.backends.database' from the INSTALLED_APPS array
# Use the database backend in dev for ease of use. We will use Redis in staging/prod.
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

# This is the dynamic config, update-able during runtime
CONSTANCE_CONFIG = {
    'LADDER_ENABLED': (
        True, 'Whether the ladder is currently enabled. This will control whether matches are run or not.'),
    'TIMEOUT_MATCHES_AFTER': (
        timedelta(hours=1),
        'How long to wait before the website should time out a running match.', timedelta),
    'MAX_ACTIVE_ROUNDS': (2, 'The maximum rounds the ladder can run simultaneously. '
                             'The ladder will stop generating new rounds once this number '
                             'is reached until previous active rounds are finished off.'),
    'REISSUE_UNFINISHED_MATCHES': (True, 'Whether to reissue previously assigned unfinished matches '
                                         'when an arena client requests a match.'),
    'BOT_CONSECUTIVE_CRASH_LIMIT': (0, 'The number of consecutive crashes after which a bot is deactivated. '
                                       'Any value below 1 will disable the check for this feature. Default: 0'),
    'MAX_USER_BOT_COUNT': (4, 'Maximum bots a user can have uploaded.'),
    'MAX_USER_BOT_COUNT_ACTIVE_PER_RACE': (1, 'Maximum active bots a user can have per race.'),
    'ARENACLIENT_DEBUG_ENABLED': (False, 'Enable debugging for arena clients. '
                                         'This will log extra data in the arena client API. '
                                         'It will also propagate the setting to the arena clients'),
    'GETTING_STARTED_URL': ('https://ai-arena.net/wiki/getting-started/',
                            'The URL to send new users to in order to get started.'),
    'DISCORD_CLIENT_ID': ('', 'Client ID used for Discord OAuth'),
    'DISCORD_CLIENT_SECRET': ('', 'Client Secret used for Discord OAuth'),
    'PATREON_CLIENT_ID': ('', 'Client ID used for Patreon OAuth'),
    'PATREON_CLIENT_SECRET': ('', 'Client Secret used for Patreon OAuth'),
    'HOUSE_BOTS_USER_ID': (0, 'The user ID of the user account which hosts all the house bots.'),
    'ALLOW_REQUESTED_MATCHES': (True, 'Whether to allow users to request matches.'),
}

CONSTANCE_CONFIG_FIELDSETS = {
    'Bots': ('MAX_USER_BOT_COUNT', 'MAX_USER_BOT_COUNT_ACTIVE_PER_RACE',),
    'General': ('ARENACLIENT_DEBUG_ENABLED', 'GETTING_STARTED_URL', 'HOUSE_BOTS_USER_ID', 'ALLOW_REQUESTED_MATCHES',),
    'Ladders': ('LADDER_ENABLED', 'MAX_ACTIVE_ROUNDS', 'TIMEOUT_MATCHES_AFTER',
                'BOT_CONSECUTIVE_CRASH_LIMIT', 'REISSUE_UNFINISHED_MATCHES',),
    'Integrations': ('DISCORD_CLIENT_ID', 'DISCORD_CLIENT_SECRET', 'PATREON_CLIENT_ID', 'PATREON_CLIENT_SECRET',)
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'django-file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': './logs/django.log',
            'formatter': 'verbose',
        },
        'aiarena-file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': './logs/aiarena.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['django-file'],
            'level': 'WARNING',
            'propagate': True,
        },
        'aiarena': {
            'handlers': ['aiarena-file'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}

WSGI_APPLICATION = 'aiarena.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")
# Don't configure this, because the files wil be automagically located
# STATICFILES_DIRS = [
#     os.path.join(APP_DIR, "frontend/static"),
# ]

# public media
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Private media storage
# https://github.com/edoburu/django-private-storage
PRIVATE_STORAGE_ROOT = os.path.join(BASE_DIR, "private-media")

# Random scripts such as SQL
SCRIPTS_ROOT = os.path.join(BASE_DIR, "scripts")

# registration
# https://django-registration-redux.readthedocs.io/en/latest/default-backend.html
ACCOUNT_ACTIVATION_DAYS = 7  # One-week activation window

# This is the default address to send emails from
DEFAULT_FROM_EMAIL = 'noreply@localhost'

# Save emails to file by default. This will be overridden in production.
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = './tmp/emails'

# Redirect to index page on login/logout
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# Custom user model
AUTH_USER_MODEL = "core.User"

# file system permissions of uploaded files
# this needs to be set, otherwise large files can end up with the wrong permissions.
# https://code.djangoproject.com/ticket/28540
FILE_UPLOAD_PERMISSIONS = 0o644

# elo_k for calculating ladder ELO updates
ELO_K = 16

# starting ELO for bots
ELO_START_VALUE = 1600

# Enable a sanity check every time a result is submitted
ENABLE_ELO_SANITY_CHECK = True

# ELO implementation
ELO = Elo(ELO_K)

# For convenience
BOT_ZIP_MAX_SIZE_MB = 50
# this is the setting that actually dictates the max zip size
BOT_ZIP_MAX_SIZE = 1024 * 1024 * BOT_ZIP_MAX_SIZE_MB

# This will post results received to another webserver
# if this is None, it is disabled
POST_SUBMITTED_RESULTS_TO_ADDRESS = None

# django-avatar
# https://django-avatar.readthedocs.io/en/latest/
# Cleanup avatar images on deletion
AVATAR_CLEANUP_DELETED = True
# disable the cache until we need it - it causes a user's avatar change to take a while to be reflected
AVATAR_CACHE_ENABLED = False
# pre-generate the most commonly used size
AVATAR_AUTO_GENERATE_SIZES = (150,)
# this fixes PNGs breaking when uploaded
AVATAR_THUMB_FORMAT = 'PNG'

AVATAR_GRAVATAR_FORCEDEFAULT = False
AVATAR_DEFAULT_URL = "/avatar/img/default.jpg"

AVATAR_PROVIDERS = (
    'avatar.providers.PrimaryAvatarProvider',
    'avatar.providers.DefaultAvatarProvider',
)


def get_discord_client_id():
    from constance import config  # so that this file can be imported without constance installed
    return config.DISCORD_CLIENT_ID


def get_discord_client_secret():
    from constance import config  # so that this file can be imported without constance installed
    return config.DISCORD_CLIENT_SECRET


DISCORD_CLIENT_ID = get_discord_client_id
DISCORD_CLIENT_SECRET = get_discord_client_secret
DISCORD_RETURN_URI = "/profile/"

ENVIRONMENT_TYPE = EnvironmentType.DEVELOPMENT

# django wiki
WIKI_ACCOUNT_HANDLING = True
WIKI_ACCOUNT_SIGNUP_ALLOWED = False
SITE_ID = 1

SITE_PROTOCOL = 'https'

# override any of these settings with an env.py file
try:
    from aiarena.env import *
except ImportError as e:
    if e.name != 'aiarena.env':
        raise

if ENVIRONMENT_TYPE != EnvironmentType.DEVELOPMENT:
    # not required in staging or production
    INSTALLED_APPS.remove('debug_toolbar')
    MIDDLEWARE.remove('debug_toolbar.middleware.DebugToolbarMiddleware')

    INSTALLED_APPS.remove('sslserver')
