from aiarena.core.utils import EnvironmentType

ENVIRONMENT_TYPE = EnvironmentType.DEVELOPMENT


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'aiarena',
        'USER': 'aiarena',
        'PASSWORD': 'aiarena',
        'HOST': 'mariadb',  # Or an IP Address that your DB is hosted on
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Remove throttling for tests.
try:
    REST_FRAMEWORK.pop('DEFAULT_THROTTLE_CLASSES', None)
    REST_FRAMEWORK.pop('DEFAULT_THROTTLE_RATES', None)
except NameError:
    pass