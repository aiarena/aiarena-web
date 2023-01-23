from aiarena.core.utils import EnvironmentType

ENVIRONMENT_TYPE = EnvironmentType.DEVELOPMENT


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'aiarena',
        'USER': 'aiarena',
        'PASSWORD': 'aiarena',
        'HOST': 'postgres',  # Or an IP Address that your DB is hosted on
        'PORT': '5432',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
