"""
Django settings for aiarena project.

Generated by 'django-admin startproject' using Django 2.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""
import os
from datetime import timedelta


# Temp workaround for discord-bind error: Warning: Scope has changed from "identify" to "guilds.join identify email".
# https://stackoverflow.com/a/51643134
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPPELLI_ADMIN_TITLE = "AiArena Admin"
GRAPPELLI_SWITCH_USER_ORIGINAL = True
GRAPPELLI_INDEX_DASHBOARD = "aiarena.frontend.dashboard.CustomIndexDashboard"
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

INTERNAL_IPS = ["127.0.0.1"]

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DATABASE", "aiarena"),
        "USER": os.getenv("POSTGRES_USER", "aiarena"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "aiarena"),
        "HOST": os.getenv("POSTGRES_HOST", "127.0.0.1"),  # set in docker-compose.yml
        "PORT": os.getenv("POSTGRES_PORT", "5432"),  # default postgres port
    },
}

# Application definition

INSTALLED_APPS = [
    "registration",
    "grappelli.dashboard",
    "grappelli",
    "django_extensions",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "django_select2",
    "avatar",
    "aiarena.core",
    "aiarena.frontend",
    "aiarena.api",
    "aiarena.patreon",
    "private_storage",
    "django.contrib.sites.apps.SitesConfig",
    "django.contrib.humanize.apps.HumanizeConfig",
    "django_nyt.apps.DjangoNytConfig",
    "mptt",
    "sekizai",
    "sorl.thumbnail",
    "wiki.apps.WikiConfig",
    "wiki.plugins.attachments.apps.AttachmentsConfig",
    "wiki.plugins.notifications.apps.NotificationsConfig",
    "wiki.plugins.images.apps.ImagesConfig",
    "wiki.plugins.macros.apps.MacrosConfig",
    "wiki.plugins.help.apps.HelpConfig",
    "constance",
    "constance.backends.database",
    "discord_bind",
    "robots",
    "django.contrib.admindocs",
    "drf_yasg",
    "django_tables2",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "aiarena.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(APP_DIR, "../frontend/templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "constance.context_processors.config",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "aiarena.frontend.context_processors.stats",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "sekizai.context_processors.sekizai",
            ],
        },
    },
]

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 100,
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    },
    "select2": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    },
}

# Tell select2 which cache configuration to use:
SELECT2_CACHE_BACKEND = "select2"
# SELECT2_CSS = ''
# Constance https://github.com/jazzband/django-constance
CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"

# This is the dynamic config, update-able during runtime
CONSTANCE_CONFIG = {
    "LADDER_ENABLED": (
        True,
        "Whether the ladder is currently enabled. This will control whether matches are run or not.",
    ),
    "TIMEOUT_MATCHES_AFTER": (
        timedelta(hours=1),
        "How long to wait before the website should time out a running match.",
        timedelta,
    ),
    "REISSUE_UNFINISHED_MATCHES": (
        True,
        "Whether to reissue previously assigned unfinished matches " "when an arena client requests a match.",
    ),
    "BOT_CONSECUTIVE_CRASH_LIMIT": (
        0,
        "The number of consecutive crashes after which a bot crash alert is triggered. "
        "Any value below 1 will disable this check. Default: 0",
    ),
    "MAX_USER_BOT_COUNT": (20, "Maximum bots a user can have uploaded."),
    "MAX_USER_BOT_PARTICIPATIONS_ACTIVE_FREE_TIER": (
        4,
        "Maximum active competition participations a free tier" " user can have at one time.",
    ),
    "MAX_USER_BOT_PARTICIPATIONS_ACTIVE_BRONZE_TIER": (
        4,
        "Maximum active competition participations a bronze tier" " user can have at one time.",
    ),
    "MAX_USER_BOT_PARTICIPATIONS_ACTIVE_SILVER_TIER": (
        8,
        "Maximum active competition participations a silver tier" " user can have at one time.",
    ),
    "MAX_USER_BOT_PARTICIPATIONS_ACTIVE_GOLD_TIER": (
        16,
        "Maximum active competition participations a gold tier" " user can have at one time.",
    ),
    "MAX_USER_BOT_PARTICIPATIONS_ACTIVE_PLATINUM_TIER": (
        32,
        "Maximum active competition participations a platinum tier" " user can have at one time.",
    ),
    "MAX_USER_BOT_PARTICIPATIONS_ACTIVE_DIAMOND_TIER": (
        9999,
        "Maximum active competition participations a diamond tier" " user can have at one time.",
    ),
    "DEBUG_LOGGING_ENABLED": (
        False,
        "Enable debug logging. "
        "This will log extra data for debugging throughout the website. "
        "It will also propagate the setting to the arena clients",
    ),
    "GETTING_STARTED_URL": (
        "https://aiarena.net/wiki/getting-started/",
        "The URL to send new users to in order to get started.",
    ),
    "DISCORD_CLIENT_ID": ("", "Client ID used for Discord OAuth"),
    "DISCORD_CLIENT_SECRET": ("", "Client Secret used for Discord OAuth"),
    "PATREON_CLIENT_ID": ("", "Client ID used for Patreon OAuth"),
    "PATREON_CLIENT_SECRET": ("", "Client Secret used for Patreon OAuth"),
    "PATREON_CREATOR_REFRESH_TOKEN": (
        "",
        "Creator refresh token for general API usage under the AI Arena credentials.",
    ),
    "HOUSE_BOTS_USER_ID": (0, "The user ID of the user account which hosts all the house bots."),
    "ALLOW_REQUESTED_MATCHES": (True, "Whether to allow users to request matches."),
    "MATCH_REQUEST_LIMIT_FREE_TIER": (30, "The periodic limit of match requests for a free patreon tier user."),
    "MATCH_REQUEST_LIMIT_BRONZE_TIER": (80, "The periodic limit of match requests for a bronze patreon tier user."),
    "MATCH_REQUEST_LIMIT_SILVER_TIER": (200, "The periodic limit of match requests for a silver patreon tier user."),
    "MATCH_REQUEST_LIMIT_GOLD_TIER": (600, "The periodic limit of match requests for a gold patreon tier user."),
    "MATCH_REQUEST_LIMIT_PLATINUM_TIER": (
        2000,
        "The periodic limit of match requests for a platinum patreon tier user.",
    ),
    "MATCH_REQUEST_LIMIT_DIAMOND_TIER": (8000, "The periodic limit of match requests for a diamond patreon tier user."),
    "MATCH_REQUESTS_PREFILL_MAP_POOL_ID": (
        0,
        "The ID of the map pool that should be selected by default " "when requesting matches.",
    ),
    "REQUESTED_MATCHES_LIMIT_PERIOD": (
        timedelta(days=30),
        "The period length for which a user" "s match request limit applies.",
        timedelta,
    ),
    "BOT_ZIP_SIZE_LIMIT_IN_MB_FREE_TIER": (
        50,
        "The maximum bot zip file size that a free supporter tier user can upload to the website.",
    ),
    "BOT_ZIP_SIZE_LIMIT_IN_MB_BRONZE_TIER": (
        100,
        "The maximum bot zip file size that a bronze supporter tier user can upload to the website.",
    ),
    "BOT_ZIP_SIZE_LIMIT_IN_MB_SILVER_TIER": (
        200,
        "The maximum bot zip file size that a silver supporter tier user can upload to the website.",
    ),
    "BOT_ZIP_SIZE_LIMIT_IN_MB_GOLD_TIER": (
        300,
        "The maximum bot zip file size that a gold supporter tier user can upload to the website.",
    ),
    "BOT_ZIP_SIZE_LIMIT_IN_MB_PLATINUM_TIER": (
        400,
        "The maximum bot zip file size that a platinum supporter tier user can upload to the website.",
    ),
    "BOT_ZIP_SIZE_LIMIT_IN_MB_DIAMOND_TIER": (
        500,
        "The maximum bot zip file size that a diamond supporter tier user can upload to the website.",
    ),
    "ELO_TREND_N_MATCHES": (30, "Number of matches to include in ELO trend calculation"),
    "ELO_DIFF_RATING_MODIFIER": (
        0.999,
        "Affects how the ELO difference between bots in an upset match "
        "(lower ranked bot beats higher ranked) affects the interest score: ELO_DIFF_RATING_MODIFIER^ELO_DIFF-1",
    ),
    "COMBINED_ELO_RATING_DIVISOR": (
        200,
        "Controls how the combined bot ELO affects the interest score: "
        "1/(1+e^(-AVG_BOT_ELO/COMBINED_ELO_RATING_DIVISOR))-0.5",
    ),
    "ENABLE_ELO_SANITY_CHECK": (
        True,
        "Whether to sanity check the total sum of bot ELO " "on result submission in order to detect ELO corruption.",
    ),
    "BOT_UPLOADS_ENABLED": (True, "Whether authors can upload new bots to the website."),
    "DISCORD_INVITE_LINK": ("", "An invite link to the Discord community server."),
    "PATREON_LINK": ("", "Link the Patreon."),
    "GITHUB_LINK": ("", "Link to GitHub."),
    "TWITCH_LINK": ("", "Link to Twitch channel."),
    "YOUTUBE_LINK": ("", "Link to YouTube."),
    "ADMIN_CLUSTER_LINK": ("", "Admin link to the cluster management."),
    "ADMIN_WEBSTATS_LINK": ("", "Admin link to view web stats."),
    "PROJECT_FINANCE_LINK": ("", "Link to the project" "s finance data."),
    "PUBLIC_BANNER_MESSAGE": ("", "Message displayed publicly at the top of the website."),
    "LOGGED_IN_BANNER_MESSAGE": ("", "Message displayed to logged in users at the top of the website."),
    "COMPETITION_PRIORITY_ORDER_CACHE_TIME": (
        3600,
        "In seconds, how long to cache the result of the AC API competition" " priority order calculation.",
    ),
}

CONSTANCE_CONFIG_FIELDSETS = {
    "Bots": (
        "BOT_UPLOADS_ENABLED",
        "MAX_USER_BOT_COUNT",
        "MAX_USER_BOT_PARTICIPATIONS_ACTIVE_FREE_TIER",
        "MAX_USER_BOT_PARTICIPATIONS_ACTIVE_BRONZE_TIER",
        "MAX_USER_BOT_PARTICIPATIONS_ACTIVE_SILVER_TIER",
        "MAX_USER_BOT_PARTICIPATIONS_ACTIVE_GOLD_TIER",
        "MAX_USER_BOT_PARTICIPATIONS_ACTIVE_PLATINUM_TIER",
        "MAX_USER_BOT_PARTICIPATIONS_ACTIVE_DIAMOND_TIER",
    ),
    "General": (
        "DEBUG_LOGGING_ENABLED",
        "GETTING_STARTED_URL",
        "HOUSE_BOTS_USER_ID",
        "ALLOW_REQUESTED_MATCHES",
        "ENABLE_ELO_SANITY_CHECK",
        "PUBLIC_BANNER_MESSAGE",
        "LOGGED_IN_BANNER_MESSAGE",
        "ELO_TREND_N_MATCHES",
    ),
    "Match Requests": (
        "MATCH_REQUEST_LIMIT_FREE_TIER",
        "MATCH_REQUEST_LIMIT_BRONZE_TIER",
        "MATCH_REQUEST_LIMIT_SILVER_TIER",
        "MATCH_REQUEST_LIMIT_GOLD_TIER",
        "MATCH_REQUEST_LIMIT_PLATINUM_TIER",
        "MATCH_REQUEST_LIMIT_DIAMOND_TIER",
        "REQUESTED_MATCHES_LIMIT_PERIOD",
        "MATCH_REQUESTS_PREFILL_MAP_POOL_ID",
    ),
    "File size limits": (
        "BOT_ZIP_SIZE_LIMIT_IN_MB_FREE_TIER",
        "BOT_ZIP_SIZE_LIMIT_IN_MB_BRONZE_TIER",
        "BOT_ZIP_SIZE_LIMIT_IN_MB_SILVER_TIER",
        "BOT_ZIP_SIZE_LIMIT_IN_MB_GOLD_TIER",
        "BOT_ZIP_SIZE_LIMIT_IN_MB_PLATINUM_TIER",
        "BOT_ZIP_SIZE_LIMIT_IN_MB_DIAMOND_TIER",
    ),
    "Ladders": (
        "LADDER_ENABLED",
        "TIMEOUT_MATCHES_AFTER",
        "BOT_CONSECUTIVE_CRASH_LIMIT",
        "REISSUE_UNFINISHED_MATCHES",
        "COMPETITION_PRIORITY_ORDER_CACHE_TIME",
    ),
    "Integrations": (
        "DISCORD_CLIENT_ID",
        "DISCORD_CLIENT_SECRET",
        "PATREON_CLIENT_ID",
        "PATREON_CLIENT_SECRET",
        "PATREON_CREATOR_REFRESH_TOKEN",
    ),
    "Match interest analysis": (
        "ELO_DIFF_RATING_MODIFIER",
        "COMBINED_ELO_RATING_DIVISOR",
    ),
    "Website links": (
        "DISCORD_INVITE_LINK",
        "PATREON_LINK",
        "GITHUB_LINK",
        "TWITCH_LINK",
        "YOUTUBE_LINK",
        "ADMIN_CLUSTER_LINK",
        "ADMIN_WEBSTATS_LINK",
        "PROJECT_FINANCE_LINK",
    ),
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": [
                "console",
            ],
            "level": "WARNING",
            "propagate": True,
        },
        "django.template": {
            "handlers": [
                "console",
            ],
            "level": "DEBUG",
            "propagate": True,
        },
        "django.security": {
            "handlers": [
                "console",
            ],
            "level": "DEBUG",
            "propagate": True,
        },
        "aiarena": {
            "handlers": [
                "console",
            ],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

WSGI_APPLICATION = "aiarena.wsgi.application"

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# public media
MEDIA_URL = "/media/"

# Random scripts such as SQL
SCRIPTS_ROOT = os.path.join(BASE_DIR, "scripts")

# registration
# https://django-registration-redux.readthedocs.io/en/latest/default-backend.html
ACCOUNT_ACTIVATION_DAYS = 7  # One-week activation window

REGISTRATION_FORM = "aiarena.frontend.forms.WebsiteUserRegistrationForm"

# This is the default address to send emails from
DEFAULT_FROM_EMAIL = "noreply@localhost"

# Save emails to file by default. This will be overridden in production.
EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = "./tmp/emails"

# Redirect to index page on login/logout
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

# Custom user model
AUTH_USER_MODEL = "core.User"

# file system permissions of uploaded files
# this needs to be set, otherwise large files can end up with the wrong permissions.
# https://code.djangoproject.com/ticket/28540
FILE_UPLOAD_PERMISSIONS = 0o644

# elo_k for calculating ladder ELO updates
ELO_K = 8

# starting ELO for bots
ELO_START_VALUE = 1600

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
AVATAR_THUMB_FORMAT = "PNG"

AVATAR_GRAVATAR_FORCEDEFAULT = False
AVATAR_DEFAULT_URL = "/avatar/img/default.jpg"

AVATAR_PROVIDERS = (
    "avatar.providers.PrimaryAvatarProvider",
    "avatar.providers.DefaultAvatarProvider",
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

# django wiki
WIKI_ACCOUNT_HANDLING = True
WIKI_ATTACHMENTS_EXTENSIONS = ["pdf", "doc", "odt", "docx", "txt", "zip"]
WIKI_ACCOUNT_SIGNUP_ALLOWED = False
SITE_ID = 1

SITE_PROTOCOL = "https"

# Match Tag Constants
MATCH_TAG_REGEX = r"[^a-z0-9 _]"
MATCH_TAG_LENGTH_LIMIT = 32
MATCH_TAG_PER_MATCH_LIMIT = 32

# If a primary field isn't specified on models, add an auto ID field. This affects all loaded modules.
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"


def str_to_bool(s):
    return s.lower() in ("yes", "y", "true", "1")


# Redis
REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "")
REDIS_USE_SSL = str_to_bool(os.environ.get("REDIS_USE_SSL", "false"))
REDIS_CELERY_DB = 0


def redis_url(db):
    if REDIS_USE_SSL:
        schema = "rediss"
        ssl_reqs = "?ssl_cert_reqs=required"
    else:
        schema = "redis"
        ssl_reqs = ""

    if not REDIS_PASSWORD:
        password = ""
    else:
        password = f":{REDIS_PASSWORD}@"

    return f"{schema}://{password}{REDIS_HOST}:{REDIS_PORT}/{db}{ssl_reqs}"


# Celery
CELERY_BROKER_URL = redis_url(REDIS_CELERY_DB)
CELERY_BROKER_TRANSPORT_OPTIONS = {
    "visibility_timeout": 3600,  # in seconds
}
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_TIMEZONE = TIME_ZONE
CELERY_ACCEPT_CONTENT = ["pickle"]
CELERY_RESULT_SERIALIZER = "pickle"
CELERY_TASK_SERIALIZER = "pickle"
CELERY_TASK_REJECT_ON_WORKER_LOST = False
CELERY_TASK_ACKS_LATE = False
CELERY_TASK_DEFAULT_QUEUE = "default"
